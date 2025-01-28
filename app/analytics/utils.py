import asyncio
from .schema import PageType, PageVisitSchema, FeedbackSpaceMetadata, SpaceType
from .model import PageVisit
from sqlalchemy.ext.asyncio import AsyncSession
from .model import PageVisit, Space, FeedbackSubmission
from sqlalchemy import select
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def calculate_new_avg(previous_avg_score, observations, new_score) -> float:
    if observations == 0:
        return new_score

    total_score = observations * previous_avg_score
    return (total_score+new_score)/(observations+1)


def get_sentiment_score(text: str) -> float:
    analyser = SentimentIntensityAnalyzer()
    sentiment = analyser.polarity_scores(text)
    return sentiment["compound"]

async def create_page_visit(session: AsyncSession, payload):
    visit = PageVisit(**payload)
    session.add(visit)


async def create_feedback_submission(session: AsyncSession, payload):
    feedback_submission = FeedbackSubmission(**payload)
    session.add(feedback_submission)


async def get_space(session: AsyncSession, space_id) -> Space:
    query = select(Space).where(Space.space_id == space_id)
    space = (await session.execute(query)).scalar()
    return space


async def create_space(session: AsyncSession, space_type: SpaceType, space_id) -> Space:
    async with session.begin_nested():
        metadata = FeedbackSpaceMetadata().model_dump(mode="json")
        space = Space(space_id=space_id, space_metadata=metadata,
                      space_type=space_type)
        session.add(space)
    await session.refresh(space)
    return space

async def get_or_create_space(session:AsyncSession, space_id: str):
    space = await get_space(session, space_id)
    if not space:
        space = await create_space(session, SpaceType.FEEDBACK, space_id)
    return space