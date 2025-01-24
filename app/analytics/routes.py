from fastapi import Depends, Query, Body, HTTPException
from typing import Annotated
from pydantic import BaseModel
from . import analytics_router
from app.db import DBSessionDep
from .schema import Event, PageVisitSchema, SpaceType
from .schema import PageVisitSchema, Event


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


@analytics_router.get("/feedback")
async def get_analytics(session: DBSessionDep, event: Event):
    return event.value
    return "hello world"


@analytics_router.post("/feedback")
async def create_analytics(session: DBSessionDep, event: Event, space:SpaceType, payload: Payload):
    if event == Event.VISIT:
        return payload