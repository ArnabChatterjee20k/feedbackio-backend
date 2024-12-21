from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import ValidationError
from ..model import Form
from ..schema import FormSchema
from .submission_utils import get_form_submission_by_ip_exists
from datetime import datetime

def get_form(session: Session, user_id=None, form_id=""):
    stmt = select(Form).filter(Form.form_id == form_id)
    if user_id:
        stmt = stmt.filter(Form.user_id == user_id)
    form = session.execute(stmt).one_or_none()
    if not form:
        return None
    data = FormSchema.model_validate(form[0],from_attributes=True).model_dump()
    return data


def create_form(session: Session, form_data):
    try:
        form = Form(**form_data)
        session.add(form)
        session.flush(form)
        return True
    except Exception as error:
        print(error)
        session.rollback()
        return False


def update_form(session: Session, form_id):
    pass


def is_form_submit_valid(session,form_id,user_ip,user_id=None):
    try:
        form = get_form(session, form_id=form_id)
        if not form:
            return False

        if form.get("close_date") and form.get("close_date") < datetime.now():
            print("date expired")
            return False

        if form.get("auth_required") and not user_id:
            print("auth required")
            return False

        if form.get("ip_required"):
            if get_form_submission_by_ip_exists(session, form_id, user_ip):
                print(f"User with IP {user_ip} has already submitted for form {form_id}.")
                return False
        
        return True
    except Exception as e:
        print(e)
        return False