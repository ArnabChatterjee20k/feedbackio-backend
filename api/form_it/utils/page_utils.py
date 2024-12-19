from ..schema import PageSchema
from ..model import Page
from sqlalchemy import select
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
def update_pages(session, pages:dict, form_id: str):
    try:
        transformed = []
        for idx, page in enumerate(pages):
            page_info = {**dict(page), "form_id": form_id, "page_order": idx+1}
            transformed.append(page_info)
        stmt = (postgresql.insert(Page).values(transformed)
                .on_conflict_do_update(
                    index_elements=["form_id","page_order"],
                    set_=dict(page)
                ))
        session.execute(stmt)
        session.commit()
        return True
    except Exception as e:
        print("Executing update stattment ",e)
        session.rollback()
        return False


def get_pages(self, form_id):
    query = select(Page).where(Page.form_id == form_id)
    result = self.session.execute(query).all()
    return [PageSchema.model_validate(page) for page in result]
