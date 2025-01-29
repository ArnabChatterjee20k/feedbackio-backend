from enum import Enum
from pydantic import BaseModel, field_serializer, field_validator, model_validator, SerializationInfo
from datetime import datetime
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
    event: Event
    ip_address: str
    country: str
    browser: str
    os: str


class PageVisitSchema(RequestMetadata):
    space_id: str
    user_id: Optional[int] = None
    page_type: PageType


class FeedbackSpaceMetadata(BaseModel):
    sentiment: Optional[float] = 0.0
    landing_page_visit: Optional[int] = 0
    wall_of_fame_visit: Optional[int] = 0
    total_feedback: Optional[int] = 0


class FeedbackSubmissionSchema(RequestMetadata):
    space_id: str
    user_id: Optional[int] = None
    feedback: str
    feedback_id: str


DATETIME_FORMAT = r"%Y-%m-%d"

# since we are raising custom errors like ValueError which are not HTTPException
# we need to catch them using app.exception_handler(ValueError)
class AnalyticsFilterQuery(BaseModel):
    start: str | None = None
    end: str | None = None
    event: Event | None = None
    visit: PageType | None = None

    @model_validator(mode="after")
    def check_duration(self):
        if self.event == Event.VISIT and not self.visit:
            raise ValueError(f"Add visit={PageType.LANDING_PAGE.value} or visit={PageType.WALL_OF_FAME.value} if event is presnt")
        if not self.start and self.end:
            raise ValueError("Start time must be present along with end")
        
        if self.start and not self.end:
            self.end = self.start
            return self
        
        # dont change start and end if they are present rather checking them in the db query and adjusting the window will be a better option
        # if self.start and self.end:
        #     start = datetime.strptime(self.start, DATETIME_FORMAT)
        #     end = datetime.strptime(self.end, DATETIME_FORMAT)
        #     # we are truncating the dates to match differnce
        #     difference = abs(start-end)
        #     if difference.days > 30:
        #         raise ValueError("Date range can't be more than 30 days")
            
        return self

    @field_validator("start", "end")
    @classmethod
    def validate(cls, value: str | str):
        if not value:
            return value
        try:
            datetime.strptime(value, DATETIME_FORMAT)
            return value
        except ValueError as e:
            raise ValueError(
                f"Invalid date format for '{value}'. Expected format: YYYY-MM-DD.")

    @field_serializer("start", "end")
    def serialise(self, value, info: SerializationInfo):
        if not value:
            return value
        if info.mode == "json":
            return value
        return datetime.strptime(value, DATETIME_FORMAT)