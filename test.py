# import asyncio
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from app.analytics.model import FeedbackSubmission
# from app.db import sessionmanager
# from datetime import datetime,time
# from sqlalchemy import func
# from sqlalchemy.dialects.postgresql import DATE

# frmt = r"%Y-%m-%d %H:%M:%S"
# parse_frmt = r"%Y-%m-%d"
# async def test():
#     curr_date = ["2025-01-31","2025-01-29","2025-01-28"]
#     for d in curr_date:
#         curr = datetime.strptime(d,parse_frmt)
#         async with sessionmanager.session() as session:
#             q = select(FeedbackSubmission).where(func.cast(FeedbackSubmission.created_at,DATE)<=curr)
#             data = await session.execute(q)
#             print(data.scalar())
    

# asyncio.run(test())

DATETIME_FORMAT = r"%Y-%m-%d"

from pydantic import BaseModel,model_validator,model_serializer,field_serializer,field_validator,SerializationInfo
from datetime import datetime

DATETIME_FORMAT = r"%Y-%m-%d"


class AnalyticsFilterQuery(BaseModel):
    start: str | None = None
    end: str | None = None
    event: str | None = None

    @model_validator(mode="after")
    def check_duration(self):
        if not self.start and self.end:
            raise ValueError("Start time must be present along with end")

        if self.start and not self.end:
            self.end = self.start

        elif self.start and self.end:
            start = datetime.strptime(self.start, DATETIME_FORMAT)
            end = datetime.strptime(self.end, DATETIME_FORMAT)
            difference = abs(start-end)
            if difference.days > 30:
                raise ValueError("Date range can't be more than 30 days")

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
        if info.mode == "json":
            return value
        return datetime.strptime(value, DATETIME_FORMAT)

curr_date = ["2025-01-31","2025-01-12","2025-01-28"]
for d in curr_date:
    print(AnalyticsFilterQuery(start=d,end=d).model_dump())
    print(AnalyticsFilterQuery(start=d).model_dump(mode="json"))
    print(AnalyticsFilterQuery(end=d).model_dump(mode="json"))