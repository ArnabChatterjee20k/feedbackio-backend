from flask import request
from api.db import Session
from . import form_it_router
from .utils.form_utils import get_form, create_form, is_form_submit_valid
from .utils.page_utils import update_pages,get_pages
from .utils.submission_utils import create_submission,get_submissions
from .schema import FormSchema, Pages, SubmissionQueryParamsSchema,Submission
from api.utils import api_response, schama_error_serialiser,get_user_id,validate_user,get_ip,validate_ip

@form_it_router.get("/<string:form_id>")
@validate_user
def get_form_controller(form_id):
    try:
        with Session() as session:
            user_id = get_user_id()
            form = get_form(session,user_id,form_id)
            if not form:
                return api_response(False, message="Not found", status=404)
            return api_response(True,data=form , status=200)
    except Exception as e:
        print("Error ",e)
        return api_response(False, message="Some error occured", status=500)

@form_it_router.post("/")
def create_form_controller():
    data = request.json
    user_id = get_user_id()
    with Session() as session:
        try:
            form_data = schama_error_serialiser(FormSchema,user_id=user_id, **data)
            if not form_data:
                return api_response(False, message="Invalid payload", status=400)

            status = create_form(session, form_data)

            if not status:
                return api_response(True, message="Error creating the form", status=500)
            session.commit()
            return api_response(True, message="Form is created", status=201)
        except Exception as e:
            print(e)
            session.rollback()
            return api_response(success=False, status=500)


@form_it_router.post("/<string:form_id>/pages")
@validate_user
def create_page_controller(form_id):
    data = request.json
    user_id = get_user_id()
    with Session() as session:
        try:
            pages = schama_error_serialiser(Pages,form_id=form_id , **data)
            if not pages:
                return api_response(False, message="Invalid payload", status=400)
            
            form = get_form(session,user_id=user_id,form_id=pages.get("form_id"))
            if not form:
                return api_response(False, message="Bad request", status=403)
            
            status = update_pages(session, pages.get("pages"), form_id = pages.get("form_id"))
            if not status:
                return api_response(False, message="Error creating pages", status=500)
            
            session.commit()
            return api_response(True, message="Pages are created", status=201)
        except Exception as e:
            print(e)
            session.rollback()
            return api_response(success=False, status=500)

# the pages can be accessed by all so thatt user can submit
@form_it_router.get("/<string:form_id>/pages")
def get_pages_controller(form_id):
    try:
        with Session() as session:
            pages = get_pages(session,form_id)
            if pages == None:
                return api_response(False, message="Not found", status=404)
            return api_response(True,data=pages, status=200)
    except Exception as e:
        print("Error ",e)
        return api_response(False, message="Some error occured", status=500)
    
@form_it_router.post("/<string:form_id>/submission")
@validate_ip
def create_submission_handler(form_id):
    ip = get_ip()
    data = request.json
    with Session() as session:
        try:
            response = schama_error_serialiser(Submission,form_id=form_id , ip=ip, submission_data = data)
            if not response:
                return api_response(False,message="Invalid payload",status=403)
            if not is_form_submit_valid(session,form_id,ip,response.get("user_id")):
                return api_response(False,message="Already submitted",status=403)
            
            submission = create_submission(session,response,form_id)

            if not submission:
                return api_response(False,message="Error submitting the form",status=500)
            
            session.commit()
            return api_response(True,message="Form Submitted",status=201)
        except Exception as e:
            session.rollback()
            print(e)
            return api_response(False,message="Some error occured",status=500)
        
@form_it_router.get("/<string:form_id>/submission")
@validate_user
def get_submission_controller(form_id):
    user_id = get_user_id()
    query_params = request.args
    params = schama_error_serialiser(SubmissionQueryParamsSchema,**query_params)

    with Session() as session:
        try:
            form = get_form(session,user_id=user_id,form_id=form_id)
            if not form:
                return api_response(False, message="Bad request", status=403)
            responses  = get_submissions(session,form_id,page=params.get("page"),limit=params.get("limit"))
            return api_response(True,data={"responses":responses})
        except Exception as e:
            print(e)
            return api_response(False,message="Some error occured",status=500)