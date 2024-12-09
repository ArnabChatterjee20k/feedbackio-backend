from pydantic import BaseModel,ValidationError
from typing import Optional
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