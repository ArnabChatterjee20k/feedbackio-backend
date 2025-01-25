from app.db import Base
from sqlalchemy import String, Integer, DateTime, Column, Enum, Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, MappedColumn
from .schema import PageType, SpaceType, UNKNOWN_DATA
from datetime import datetime
from sqlalchemy.sql import func

class Space(Base):
    __tablename__ = "spaces"
    id: MappedColumn[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    space_id: MappedColumn[str] = mapped_column(unique=True, nullable=False)
    space_metadata = Column(JSONB, nullable=False) # page visits, avg sentiment score,etc
    space_type: MappedColumn[str] = Column(Enum(SpaceType), nullable=False)
    updated_at: MappedColumn[datetime] = Column(DateTime, default=datetime.now,onupdate=func.now())
    created_at: MappedColumn[datetime] = Column(DateTime, default=datetime.now)


class PageVisit(Base):
    __tablename__ = "page_visits"
    id: MappedColumn[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    space_id: MappedColumn[str] = mapped_column(nullable=False)
    page_type: MappedColumn[str] = mapped_column(
        Enum(PageType), nullable=False)
    user_id: MappedColumn[str|None] = mapped_column(nullable=True)
    ip_address = Column(String(45), nullable=False, default=UNKNOWN_DATA)
    country = Column(String(50), nullable=True, default=UNKNOWN_DATA)
    browser = Column(String(50), nullable=True, default=UNKNOWN_DATA)
    os = Column(String(50), nullable=True, default=UNKNOWN_DATA)
    visited_at = Column(DateTime, default=datetime.now)

    @hybrid_property
    def is_user_loggedin(self) -> bool:
        return bool(self.user_id)

class FeedbackSubmission(Base):
    __tablename__ = "feedback_submission"
    id: MappedColumn[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    space_id: MappedColumn[str] = mapped_column(nullable=False)
    user_id: MappedColumn[str|None] = mapped_column(nullable=True)
    avg_sentiment_score:MappedColumn[float] = mapped_column(Float,nullable=False)
    ip_address = Column(String(45), nullable=False, default=UNKNOWN_DATA)
    country = Column(String(50), nullable=True, default=UNKNOWN_DATA)
    browser = Column(String(50), nullable=True, default=UNKNOWN_DATA)
    os = Column(String(50), nullable=True, default=UNKNOWN_DATA)
    created_at = Column(DateTime, default=datetime.now)

    @hybrid_property
    def is_user_loggedin(self) -> bool:
        return bool(self.user_id)