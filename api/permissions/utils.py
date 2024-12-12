from api.db import Session
from .model import Permissions
from sqlalchemy import select, func


def create_permission(permissions: dict):
    with Session() as session:
        with session.begin():
            try:
                new_permissions = [Permissions(
                    **permission) for permission in permissions]
                session.bulk_save_objects(new_permissions)
                return True
            except Exception as e:
                session.rollback()
                print(e)
                return False

# we cant lock rows(for update) during aggregations
def get_permission(document_id, user_id=None):
    try:
        with Session() as session:
            with session.begin():
                query = (
                    select(Permissions.user_id,
                        func.array_agg(Permissions.permission).label("permissions"))
                    .where(Permissions.document_id == document_id)
                )
                if user_id:
                    query = query.where(Permissions.user_id == user_id)
                query = query.group_by(Permissions.user_id)
                # using execute as we need multiple columns
                permission_info = session.execute(query).all()
                permission_data = [
                    {"user_id": permission.user_id,
                    "permissions": [perm.value for perm in permission.permissions]}
                    for permission in permission_info
                ]
                return permission_data, False
    except Exception as e:
        print(e)
        return None, True


def delete_permission(permission: dict):
    try:
        with Session() as session:
            document_id = permission.get("document_id")
            user_id = permission.get("user_id")
            permission_type = permission.get("permission")
            document_type = permission.get("type")
            permission_query = select(Permissions).where(Permissions.document_id == document_id
                                                         and Permissions.user_id == user_id
                                                         and Permissions.permission == permission_type
                                                         and Permissions.type == document_type)
            permission_row = session.scalar(permission_query)
            if not permission_row:
                return False, "permission does not exists"
            session.delete(permission_row)
            session.commit()
            return True, None
    except Exception as e:
        print(e)
        return False, "Some error occured"
