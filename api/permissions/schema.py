from pydantic import BaseModel
from .model import Permission,Type
from typing import Optional
class PermissionSchema(BaseModel):
    user_id:str
    document_id:str
    permission:Optional[Permission] = Permission.READ
    type:Optional[Type]


class PermissionsListSchema(BaseModel):
    permissions:list[PermissionSchema]

class DeletePermissionSchema(PermissionSchema):
    type:Type
    permission:Permission