from pydantic import BaseModel,ValidationError
from flask import request
from werkzeug.exceptions import Forbidden
from typing import Optional
from functools import wraps
import os
def schama_error_serialiser(Schema:BaseModel,user=False,*args,**kwargs) -> Optional[dict]:
    try:
        data:BaseModel = Schema(*args,**kwargs)
        return data.model_dump()
    except ValidationError as e:
        print(e)
        return None


def api_response(success:bool,data=None,message="",status=200):
    response = {"success":success}
    if data!=None:
        response["data"] = data
    if message:
        response["message"] = message
    
    return response,status


def is_valid_request():
    token = request.headers.get("X-FEEDBACK-AUTH-TOKEN")
    print(token,os.environ.get("X-FEEDBACK-AUTH-TOKEN"))
    if not token:
        return False  # Return False if no token is provided
    
    is_valid = token == os.environ.get("X-FEEDBACK-AUTH-TOKEN")
    
    print(is_valid)
    
    return is_valid

def get_user_id():
    user_id = request.headers.get("X-AUTH-ID")
    if not user_id:
        return None
    return user_id

def validate_user(f):
    @wraps(f)
    def inner(*args, **kwargs):
        user = get_user_id()
        if not user:
            return api_response(success=False, message="X-AUTH-ID not present", status=403)
        return f(*args, **kwargs)  # Pass along the arguments to the decorated function
    return inner