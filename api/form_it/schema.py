from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict,Union
from enum import Enum

class FieldVariant(str, Enum):
    checkbox = "Checkbox"
    combobox = "Combobox"
    date_picker = "Date Picker"
    file_input = "File Input"
    datetime_picker = "Datetime Picker"
    multi_select = "Multi Select"
    phone = "Phone"
    select = "Select"
    slider = "Slider"
    textarea = "Textarea"
    tags_input = "Tags Input"
    images = "images"

class Field(BaseModel):
    checked: bool
    description: str
    disabled: bool
    label: str
    name: str
    placeholder: str
    required: bool
    rowIndex: int
    value: Optional[str] = None
    variant: FieldVariant
    options: Optional[List[str]] = None

    class Config:
        from_attributes = True

class PageSchema(BaseModel):
    title: Optional[str]
    fields: Dict[str,Field]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class PageSerialiserSchema(PageSchema):
    page_order:int

class Pages(BaseModel):
    pages: List[PageSchema]
    form_id:str

    class Config:
        from_attributes = True


class FormSchema(BaseModel):
    name: str
    form_id:str
    user_id:str
    close_date: Optional[datetime] = None
    auth_required:Optional[bool] = False
    ip_required:Optional[bool] = False
    discord_notification:Optional[bool] = False
    
    pages:Optional[List[PageSchema]] = []

    class Config:
        from_attributes = True


class Submission(BaseModel):
    submission_data: Dict[str, str]
    user_id:Optional[str]=None
    ip:str


class SubmissionQueryParamsSchema(BaseModel):
    page:Optional[int] = 1
    limit:Optional[int] = 50