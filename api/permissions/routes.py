from flask import request
from . import permission_router
from api.utils import schama_error_serialiser,api_response
from werkzeug.exceptions import BadRequest,InternalServerError,NotFound
from .schema import PermissionsListSchema,DeletePermissionSchema
from .utils import create_permission,get_permission,delete_permission
@permission_router.post("/")
def create():
    data = request.json
    permission_data = schama_error_serialiser(PermissionsListSchema,**data)
    try:
        if not permission_data:
            return api_response(False,message="Invalid payload",status=400)
        status = create_permission(permission_data.get("permissions"))
        if not status:
            return api_response(False,message="Failed to create permission",status=500)
        return api_response(True,message="Permissions are created",status=201)
    except Exception as e:
        print(e)
        return api_response(False,message="Failed to create permission",status=500)

@permission_router.get("/")
def get_permission_info():
    document_id = request.args.get("document_id")
    user_id = request.args.get("user_id")
    if not document_id:
        return api_response(False,message="Invalid payload",status=400)
    try:
        permission,error = get_permission(document_id,user_id)
        if error:
            return api_response(False,message="Failed to get permission",status=500)
        if not permission:
            return api_response(True,data=[],status=404)
        return api_response(True,data=permission,status=200)

    except Exception as e:
        print(e)
        return api_response(False,message="Failed to create permission",status=500)
    
@permission_router.delete("/")
def delete_permission_info():
    data = request.json
    
    validated_data = schama_error_serialiser(DeletePermissionSchema, **data)
    if not validated_data:
        return api_response(False, "Invalid request payload", status=400)
    
    try:
        deleted, error = delete_permission(validated_data)
        
        if error:
            return api_response(False, "Error deleting permission", status=400)
        
        if not deleted:
            return api_response(False, "Permission not found", status=404)
        
        return api_response(True, "Permission deleted successfully", status=200)
    
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return api_response(False, message="Internal Server Error", data={"error": str(e)}, status=500)