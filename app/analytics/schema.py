from enum import Enum
from pydantic import BaseModel
from typing import Optional
class SpaceType(Enum):
    FEEDBACK = "feedback"

class PageType(Enum):
    LANDING_PAGE = "landing page"
    WALL_OF_FAME = "wall of fame"

UNKNOWN_DATA = "unknown"

class Event(Enum):
    VISIT = "visit"
    SUBMIT = "submit"

class RequestMetadata(BaseModel):
    ip_address:str
    country:str
    browser:str
    os:str

class PageVisitSchema(RequestMetadata):
    space_id:str
    user_id:Optional[int] = None
    page_type:PageType

class FeedbackSpaceMetadata(BaseModel):
    sentiment:Optional[float] = 0.0
    landing_page_visit:Optional[int] = 0
    wall_of_fame_visit:Optional[int] = 0
    total_feedback:Optional[int] = 0

class FeedbackSubmissionSchema(RequestMetadata):
    space_id:str
    user_id:Optional[int] = None
    feedback:str
    feedback_id:str