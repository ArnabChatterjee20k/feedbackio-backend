from sqlalchemy.orm import Session
from pydantic import ValidationError
from ..model import Form
from ..schema import FormSchema


def get_form(session: Session, form_id):
    form = session.get(Form, form_id)
    data = FormSchema.model_validate(form).model_dump()
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
