from pydantic import BaseModel,ValidationError
from flask import request
from werkzeug.exceptions import Forbidden
from typing import Optional
import os
def schama_error_serialiser(Schema:BaseModel,*args,**kwargs) -> Optional[dict]:
    try:
        data:BaseModel = Schema(*args,**kwargs)
        return data.dict()
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
    if bool(os.environ.get("PROD")!="1"):
        return True
    token = request.headers.get("X-FEEDBACK-AUTH-TOKEN")
    print(token,os.environ.get("X-FEEDBACK-AUTH-TOKEN"))
    if not token:
        return False  # Return False if no token is provided
    
    is_valid = token == os.environ.get("X-FEEDBACK-AUTH-TOKEN")
    
    print(is_valid)
    
    return is_valid