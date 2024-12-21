from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import ValidationError
from ..model import Form
from ..schema import FormSchema


def get_form(session: Session, user_id, form_id):
    stmt = select(Form).filter(Form.form_id == form_id , Form.user_id == user_id)
    form = session.execute(stmt).one_or_none()
    if not form:
        return None
    data = FormSchema.model_validate(form[0],from_attributes=True).model_dump()
    return data


def create_form(session: Session, form_data):
    try:
        form = Form(**form_data)
        session.add(form)
        return True
    except ValidationError as error:
        session.rollback()
        return False


def update_form(session: Session, form_id):
    pass
