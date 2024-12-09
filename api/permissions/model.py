from api.db import Base
from sqlalchemy import String,Integer,DateTime,Enum,Column,UniqueConstraint
from sqlalchemy.orm import mapped_column,Mapped
from datetime import datetime
import enum

class Permission(enum.Enum):
    READ = "read"
    # write and update are same
    WRITE = "write"
    DELETE = "delete"

class Type(enum.Enum):
    FEEDBACK = "feedback"
    POLL = "poll"

class Permissions(Base):
    __tablename__ = "permissions"
    id:Mapped[int] = mapped_column("id",autoincrement=True,nullable=False,primary_key=True)
    user_id:Mapped[str] = mapped_column("user_id",nullable=False)
    document_id:Mapped[str] = mapped_column("document_id",nullable=False)
    permission = Column("permission",Enum(Permission),default=Permission.READ)
    type = Column("type",Enum(Type),nullable=False)
    created_at = Column("created_at",DateTime(),default=datetime.now)

    # setting a combination unique column
    __table_args__=(
        UniqueConstraint("user_id","document_id","permission","type",name="unique_permission"),
    )