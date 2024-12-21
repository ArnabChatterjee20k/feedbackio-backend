from flask import request
from api.db import Session
from . import form_it_router
from .utils.form_utils import get_form, create_form
from .utils.page_utils import update_pages,get_pages
from .schema import FormSchema, Pages
from api.utils import api_response, schama_error_serialiser,get_user_id,validate_user

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
            
            status = update_pages(session, pages.get("pages"), data.get("form_id"))
            if not status:
                return api_response(False, message="Error creating pages", status=500)
            
            session.commit()
            return api_response(True, message="Pages are created", status=201)
        except Exception as e:
            print(e)
            session.rollback()
            return api_response(success=False, status=500)

@form_it_router.get("/<string:form_id>/pages")
@validate_user
def get_pages_controller(form_id):
    user_id = get_user_id()
    try:
        with Session() as session:
            form = get_form(session,user_id,form_id)
            
            if not form:
                return api_response(False, message="Bad request", status=403)
            
            pages = get_pages(session,form_id)
            if pages == None:
                return api_response(False, message="Not found", status=404)
            return api_response(True,data=pages, status=200)
    except Exception as e:
        print("Error ",e)
        return api_response(False, message="Some error occured", status=500)