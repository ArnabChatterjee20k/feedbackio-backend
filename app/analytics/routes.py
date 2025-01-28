import asyncio
from fastapi import Depends, Query, Body, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from pydantic import BaseModel
from . import analytics_router
from app.db import DBSessionDep
from .schema import Event, PageVisitSchema
from .schema import PageVisitSchema, Event, SpaceType, FeedbackSpaceMetadata, PageType, FeedbackSubmissionSchema
from .utils import get_or_create_space, create_page_visit, create_feedback_submission, get_sentiment_score, calculate_new_avg
from app.logger import get_logger


def get_schema(
    payload: dict = Body(...)
) -> BaseModel:
    try:
        event = payload.get("event")
        if not event:
            raise HTTPException(
                status_code=400, detail=f"Event type not provided")
        if event == Event.VISIT.value:
            print(payload)
            return PageVisitSchema(**payload)
        elif event == Event.SUBMIT.value:
            return FeedbackSubmissionSchema(**payload)
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported event type: {event}")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid payload for event {event}: {e}")


Payload = Annotated[BaseModel, Depends(get_schema)]
logger = get_logger()

# example -> /<resource>?event=visit =>/feedback?event=visit


@analytics_router.post("/feedback")
async def create_feedback_analytics(session: DBSessionDep, payload: Payload):
    try:
        event = payload.event
        if event == Event.VISIT:
            """
                space metadata update ; {visit+=1}
                page visit logging
            """
            async with session.begin():
                data: PageVisitSchema = payload
                space = await get_or_create_space(session, data.space_id)
                space_metadata = FeedbackSpaceMetadata(**space.space_metadata)
                if data.page_type == PageType.LANDING_PAGE:
                    space_metadata.landing_page_visit += 1
                elif data.page_type == PageType.WALL_OF_FAME:
                    space_metadata.wall_of_fame_visit += 1
                space.space_metadata = space_metadata.model_dump()
                new_payload = {key: value for key, value in data.model_dump().items() if key != "event"}
                await create_page_visit(session, new_payload)
                await session.commit()

        elif event == Event.SUBMIT:
            """
                space metadata update ; {avg sentiment score}
                feedback submission
            """
            data: FeedbackSubmissionSchema = payload
            async with session.begin():
                space = await get_or_create_space(session, data.space_id)
                space_metadata = FeedbackSpaceMetadata(**space.space_metadata)
                feedback_sentiment_score = await asyncio.to_thread(lambda: get_sentiment_score(data.feedback))
                space_sentiment_score = calculate_new_avg(
                    space_metadata.sentiment, space_metadata.total_feedback, feedback_sentiment_score)

                space_metadata.sentiment = space_sentiment_score
                space_metadata.total_feedback += 1
                space.space_metadata = space_metadata.model_dump()

                new_payload = {
                    key: value for key, value in data.model_dump().items() if key not in ("feedback","event")}
                new_payload["sentiment_score"] = feedback_sentiment_score
                await create_feedback_submission(session, new_payload)
                await session.commit()
                return JSONResponse({"success": True, "sentiment": feedback_sentiment_score}, 201)
        return JSONResponse({"success": True}, 201)
    except Exception as e:
        logger.error(f"{event}", e)
        return JSONResponse({"success": False}, 500)


@analytics_router.get("/feedback")
async def get_feedback_analytics(session: DBSessionDep, event: Event):
    return event.value
