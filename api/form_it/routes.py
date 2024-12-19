from flask import request
from api.db import Session
from . import form_it_router
from .utils.form_utils import get_form, create_form
from .utils.page_utils import update_pages
from .schema import FormSchema, Pages
from api.utils import api_response, schama_error_serialiser


@form_it_router.post("/")
def create_form_controller():
    data = request.json
    with Session() as session:
        try:
            form_data = schama_error_serialiser(FormSchema, **data)
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


@form_it_router.post("/pages")
def create_page_controller():
    data = request.json
    with Session() as session:
        try:
            pages = schama_error_serialiser(Pages, **data)
            if not pages:
                return api_response(False, message="Invalid payload", status=400)
            status = update_pages(session, pages.get("pages"), data.get("form_id"))
            if not status:
                return api_response(True, message="Error creating pages", status=500)
            session.commit()
            return api_response(True, message="Pages are created", status=201)
        except Exception as e:
            print(e)
            session.rollback()
            return api_response(success=False, status=500)
