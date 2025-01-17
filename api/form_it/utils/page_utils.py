from ..schema import PageSerialiserSchema
from ..model import Page,Form
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import Session
from sqlalchemy.dialects import postgresql

import random
import string

# TODO: look here to implement it properly so that in future
# May be taking id from the api call can help having the users to know the uuid as well


def transform_to_kv(data):
    fields = {}
    for field in data:
        random_suffix = "".join(random.choices(string.ascii_letters, k=10))
        random_name = f"{field.get('name')}_{random_suffix}"
        fields[random_name] = field
    return fields


# a json of fields will be supplied here with the field id from the api itself to track that down
# use the page count to detect page deleted
def update_pages(session: Session, pages: dict, form_id: str):
    try:
        # locking the form row
        form = session.execute(
            select(Form)
            .where(Form.form_id == form_id)
            .with_for_update()  # This adds SELECT FOR UPDATE
        ).scalar_one()

        # locking the page rows
        existing_pages = session.execute(
            select(Page)
            .where(Page.form_id == form_id)
            .with_for_update()  # This locks the rows
        ).scalars().all()

        transformed = []
        for idx, page in enumerate(pages):
            page_info = {**dict(page), "form_id": form_id, "page_order": idx+1}
            transformed.append(page_info)
        insert_stmt = postgresql.insert(Page).values(transformed)
        upsert_stmt = (insert_stmt
                .on_conflict_do_update(
                    index_elements=["form_id", "page_order"],
                    set_={
                        column.name : getattr(insert_stmt.excluded,column.name) 
                        for column in Page.__table__.columns
                        if column.name not in ["form_id", "page_order"]
                    }
        ))
        session.execute(upsert_stmt)
        current_pages = set([page.page_order for page in existing_pages])
        new_pages = set([page["page_order"] for page in transformed])
        deleted_pages = current_pages - new_pages

        if deleted_pages:
            delete_stmt = delete(Page).where(
                and_(
                    Page.page_order.in_(deleted_pages),
                    Page.form_id == form_id
                )
            )
            session.execute(delete_stmt)
        return True
    except Exception as e:
        print("Executing update stattment ", e)
        session.rollback()
        return False


def get_pages(session: Session, form_id):
    try:
        print(form_id)
        query = select(Page).where(
            Page.form_id == form_id).order_by(Page.page_order)
        result = session.execute(query).all()
        return [PageSerialiserSchema.model_validate(page[0], from_attributes=True).model_dump() for page in result]

    except Exception as e:
        print(e)
        session.rollback()
        return None
