import pytest
from api.db import Session, Base
from api.permissions.model import Permissions
from api.permissions.utils import create_permission, get_permission, delete_permission
from api.permissions.schema import PermissionSchema, DeletePermissionSchema
from api.permissions.model import Permission, Type


# ----------------------- FIXTURES ----------------------- #

@pytest.fixture(scope="function")
def session():
    """Provides a new database session for each test."""
    db_session = Session()
    yield db_session
    db_session.rollback()
    db_session.close()


# ----------------------- TEST CASES ----------------------- #

# Test create_permission
def test_create_permission(session):
    permissions = [
        PermissionSchema(
            document_id="doc1", user_id="user1", permission=Permission.READ, type=Type.FEEDBACK
        ).dict(),
        PermissionSchema(
            document_id="doc2", user_id="user2", permission=Permission.WRITE, type=Type.POLL
        ).dict(),
    ]
    status = create_permission(permissions)
    assert status is True

    saved_permissions = session.query(Permissions).all()
    assert len(saved_permissions)!=0
    assert len(saved_permissions)!=None


# Test get_permission
def test_get_permission(session):
    # Pre-populate data
    session.add(
        Permissions(
            document_id="doc1", user_id="user1", permission=Permission.READ, type=Type.FEEDBACK
        )
    )
    session.commit()

    permissions, error = get_permission("doc1", "user1")
    assert error is False
    assert permissions[0]["user_id"] == "user1"
    assert permissions[0]["permission"].value == Permission.READ.value
    assert permissions[0]["type"].value == str(Type.FEEDBACK)

    # Test non-existent permission
    permissions, error = get_permission("non_existent_doc", "user1")
    assert permissions == []
    assert error is False


# Test delete_permission
def test_delete_permission(session):
    # Pre-populate data
    permission = [PermissionSchema(
        document_id="doc1", user_id="user1", permission=Permission.READ, type=Type.FEEDBACK
    ).dict()]

    status = create_permission(permission)
    assert status == True

    # Test successful deletion
    delete_data = DeletePermissionSchema(
        document_id="doc1", user_id="user1", permission=Permission.READ, type=Type.FEEDBACK
    ).dict()
    status, msg = delete_permission(delete_data)
    assert status is True
    assert msg is None
