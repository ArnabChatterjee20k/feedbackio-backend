from fastapi import Depends, Query, Body, HTTPException
from typing import Annotated
from pydantic import BaseModel
from . import analytics_router
from app.db import DBSessionDep
from .schema import Event, PageVisitSchema
from .schema import PageVisitSchema, Event, SpaceType, FeedbackSpaceMetadata, PageType
from .utils import create_space, get_space, create_page_visit
from app.logger import get_logger


def get_schema(
    event: Event = Query(..., description="Event type to determine schema"),
    payload: dict = Body(...)
) -> BaseModel:
    try:
        if event == Event.VISIT:
            return PageVisitSchema(**payload)
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported event type: {event}")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid payload for event {event}: {e}")


Payload = Annotated[BaseModel, Depends(get_schema)]
logger = get_logger()

@analytics_router.post("/feedback")
async def create_feedback_analytics(session: DBSessionDep, event: Event, payload: Payload):
    try:
        if event == Event.VISIT:
            """
                space metadata update ; {visit+=1}
                page visit logging
            """
            async with session.begin():
                    data: PageVisitSchema = payload
                    space = await get_space(session, data.space_id)
                    if not space:
                        space = await create_space(
                            session, SpaceType.FEEDBACK, data.space_id)
                    space_metadata = FeedbackSpaceMetadata(**space.space_metadata)
                    if data.page_type == PageType.LANDING_PAGE:
                        space_metadata.landing_page_visit += 1
                    elif data.page_type == PageType.WALL_OF_FAME:
                        space_metadata.wall_of_fame_visit += 1
                    space.space_metadata = space_metadata.model_dump()
                    await create_page_visit(session,data.model_dump())
                    await session.commit()
                    return {"success":True}
    except Exception as e:
        logger.error(f"{event}",e)
        return {"success":False}

# example -> /<resource>?event=visit =>/feedback?event=visit


@analytics_router.get("/feedback")
async def get_feedback_analytics(session: DBSessionDep, event: Event):
    return event.value