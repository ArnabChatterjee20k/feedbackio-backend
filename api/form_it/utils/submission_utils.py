from sqlalchemy.orm import Session
from sqlalchemy import select
from ..model import FormSubmission
from ..schema import Submission
from api.utils import get_paginated_data

def get_submissions(session:Session,form_id,page,limit):
    try:
        stmt = select(FormSubmission).filter(FormSubmission.form_id==form_id)
        data = get_paginated_data(session=session,query=stmt,page=page,limit=limit)
        if not data:
            return []
        results = [Submission.model_validate(submission[0],from_attributes=True).model_dump() for submission in data]
        return results
    except Exception as e:
        print(e)
        session.rollback()
        return None
    

def create_submission(session:Session,data,form_id):
    try:
        submission = FormSubmission(**data,form_id=form_id)
        session.add(submission)
        session.flush()
        session.refresh(submission)
        return Submission.model_validate(submission,from_attributes=True).model_dump()
    except Exception as e:
        print("Error creating submission ",e)
        session.rollback()
        return None
    
def get_form_submission_by_ip_exists(session:Session,form_id,user_ip):
    try:
        submission = session.execute(
            select(FormSubmission)
            .filter_by(form_id=form_id, ip=user_ip)
        ).first()
        return bool(submission)
    except Exception as e:
        print(f"Error querying form submissions by IP: {e}")
        return True