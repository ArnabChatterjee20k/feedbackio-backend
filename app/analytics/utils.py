import asyncio
from .schema import PageType, PageVisitSchema, FeedbackSpaceMetadata, SpaceType, DATETIME_FORMAT
from app.db import sessionmanager
from sqlalchemy.ext.asyncio import AsyncSession
from .model import PageVisit, Space, FeedbackSubmission
from sqlalchemy import select, and_, distinct, func
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.dialects.postgresql import insert, DATE
from datetime import datetime, timedelta


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


async def get_space(session: AsyncSession, space_id, lock=True) -> Space:
    query = select(Space).where(Space.space_id == space_id)
    if lock:
        query = query.with_for_update()
    space = (await session.execute(query)).scalar()
    return space


async def create_space(session: AsyncSession, space_type: SpaceType, space_id) -> Space:
    async with session.begin_nested():
        metadata = FeedbackSpaceMetadata().model_dump(mode="json")
        insert_stmt = insert(Space).values(space_id=space_id, space_metadata=metadata,
                                           space_type=space_type)
        upsert = insert_stmt.on_conflict_do_nothing(
            index_elements=[Space.space_id])
        await session.execute(upsert)

        query = select(Space).where(Space.space_id == space_id)
        space = (await session.execute(query)).scalar_one_or_none()
        return space


async def get_or_create_space(session: AsyncSession, space_id: str):
    space = await get_space(session, space_id)
    if not space:
        space = await create_space(session, SpaceType.FEEDBACK, space_id)
    return space

def parse_start_end(start:datetime,end:datetime):
    if not start:
        start = datetime.now()
        end = datetime.now()
    date_difference = abs(start-end).days
    if date_difference == 0:
        end = start + timedelta(hours=24)

    if start > end:
        end = start + timedelta(hours=24)

    # data will not be shown more than 60 days
    if date_difference > 60:
        end = start + timedelta(days=60)

    return start,end

# for getting browsers,countires,etc especially the metadatas
async def get_analytics_metadata(Model, *filters):
    """ 
        Having a shared session can cause issues here as 
        we cant use shared session if all the r equests with same shared session is made
        So each individual requests should use a separate
        That's why feedback_data is having their separate session instance
    """
    METADATA_KEYS=["country", "browser", "os"]
    date_check = and_(*filters)
    async def get_data(group_by_column):
        async with sessionmanager.session() as session:
            query = select(group_by_column, func.count(group_by_column))
            if filters:
                query = query .where(date_check)
            query = query.group_by(group_by_column)
            result = await session.execute(query)
            response = {}
            for col, val in result.all():
                response[col] = val

            return response
    
    queries = []
    for metadata in METADATA_KEYS:
        property = getattr(Model,metadata,None)
        if property:
            queries.append(get_data(property))
    if not queries:
        return []
    data = await asyncio.gather(*queries)
    return data


async def get_feedback_submission_between_range(space_id: str, start: datetime, end: datetime):
    start,end = parse_start_end(start,end)
    async with sessionmanager.session() as session:
        date_casted_created_at_col = func.cast(
            FeedbackSubmission.created_at, DATE)
        query = select(FeedbackSubmission.created_at, func.count()).where(and_(
            FeedbackSubmission.space_id == space_id,
            date_casted_created_at_col >= start,
            date_casted_created_at_col <= end
        )
        ).group_by(FeedbackSubmission.created_at)
        response = {}
        feedbacks = (await session.execute(query)).all()
        for created_at, count in feedbacks:
            created_at = created_at.strftime(DATETIME_FORMAT)
            # we are parsing date part so in one date there can be multiple submission
            # so we are doing addition
            if created_at in response:
                response[created_at] += count
            else:
                response[created_at] = count
        return response


async def get_feedback_submission_metadata(space_id: str, start: datetime, end: datetime):
    start,end = parse_start_end(start,end)

    # Date range filter
    date_casted_created_at_col = func.cast(FeedbackSubmission.created_at, DATE)
    date_check = and_(
        FeedbackSubmission.space_id == space_id,
        date_casted_created_at_col >= start,
        date_casted_created_at_col <= end
    )

    countries, browsers, os = await get_analytics_metadata(FeedbackSubmission,date_check)

    return {"countries": countries, "browsers": browsers, "os": os}


async def get_page_visits_between_range(space_id:str,start:datetime,end:datetime,page_type:str):
    start,end = parse_start_end(start,end)
    page_type_query = []

    if page_type == PageType.LANDING_PAGE:
        page_type_query.append(PageVisit.page_type == PageType.LANDING_PAGE)

    elif page_type == PageType.WALL_OF_FAME:
        page_type_query.append(PageVisit.page_type == PageType.WALL_OF_FAME)
    
    else:
        return []

    async with sessionmanager.session() as session:
        date_casted_created_at_col = func.cast(
            PageVisit.visited_at, DATE)
        query = select(PageVisit.visited_at, func.count()).where(and_(
            PageVisit.space_id == space_id,
            date_casted_created_at_col >= start,
            date_casted_created_at_col <= end,
            *page_type_query
        )
        ).group_by(PageVisit.visited_at)
        response = {}
        feedbacks = (await session.execute(query)).all()
        for created_at, count in feedbacks:
            created_at = created_at.strftime(DATETIME_FORMAT)
            # we are parsing date part so in one date there can be multiple submission
            # so we are doing addition
            if created_at in response:
                response[created_at] += count
            else:
                response[created_at] = count
        return response
    
async def get_page_visit_metadata(space_id: str, start: datetime, end: datetime):
    start,end = parse_start_end(start,end)

    # Date range filter
    date_casted_created_at_col = func.cast(PageVisit.visited_at, DATE)
    date_check = and_(
        PageVisit.space_id == space_id,
        date_casted_created_at_col >= start,
        date_casted_created_at_col <= end
    )

    countries, browsers, os = await get_analytics_metadata(PageVisit,date_check)

    return {"countries": countries, "browsers": browsers, "os": os}