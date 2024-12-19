from datetime import datetime
from typing import Optional
from api.db import Base
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import MappedColumn, mapped_column, relationship


class Form(Base):
    __tablename__ = 'forms'

    id: MappedColumn[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    form_id: MappedColumn[str] = mapped_column(
        String, unique=True, nullable=False)
    name: MappedColumn[str] = mapped_column(String(100), nullable=False)

    created_at: MappedColumn[datetime] = mapped_column(
        DateTime, default=datetime.now)
    close_date: MappedColumn[Optional[datetime]
                             ] = mapped_column(DateTime, nullable=True)

    pages_count: MappedColumn[int] = mapped_column(Integer, nullable=False)

    layout: MappedColumn[str] = mapped_column(
        String(10), nullable=True)  # Page Forms, Survey forms

    auth_required: MappedColumn[bool] = mapped_column(
        Boolean, nullable=False, default=False)
    ip_required: MappedColumn[bool] = mapped_column(
        Boolean, nullable=False, default=False)
    discord_notification: MappedColumn[bool] = mapped_column(
        Boolean, nullable=False, default=False)
    pages = relationship('Page', back_populates='form',
                         cascade="all, delete-orphan")

    submissions = relationship(
        'FormSubmission', back_populates='form', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Form(id={self.id}, name={self.name})>"


class Page(Base):
    __tablename__ = 'form-pages'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_id = mapped_column(String, ForeignKey(
        'forms.form_id'), nullable=False)
    title = mapped_column(String(100), nullable=True)
    description = mapped_column(Text, nullable=True)
    page_order = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime, default=datetime.now)

    form = relationship('Form', back_populates='pages')
    fields = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        UniqueConstraint("form_id", "page_order", name="unique_page"),
    )

    def __repr__(self):
        return f"<Page(id={self.id}, form_id={self.form_id}, title={self.title})>"


class FormSubmission(Base):
    __tablename__ = 'form-submission'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_id = mapped_column(String, ForeignKey(
        'forms.form_id'), nullable=False)
    submitted_at = mapped_column(DateTime, default=datetime.now)
    # JSONB for submitted form data
    submission_data = mapped_column(JSONB, nullable=False)
    user_id = mapped_column(String, nullable=True)
    ip = mapped_column(String, nullable=False)
    form = relationship('Form', back_populates='submissions')

    def __repr__(self):
        return f"<FormSubmission(id={self.id}, form_id={self.form_id}, submitted_at={self.submitted_at})>"
