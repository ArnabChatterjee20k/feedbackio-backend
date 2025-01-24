from .schema import PageType, PageVisitSchema, FeedbackSpaceMetadata, SpaceType
from .model import PageVisit
from sqlalchemy.ext.asyncio import AsyncSession
from .model import PageVisit, Space
from sqlalchemy import select


async def record_page_visit(session: AsyncSession, payload: PageVisitSchema):
    visit = PageVisit(**payload)
    session.add(visit)


async def get_space(session: AsyncSession, space_id) -> Space:
    query = select(Space).where(Space.space_id == space_id)
    space = (await session.execute(query)).scalar()
    return space


async def create_space(session: AsyncSession, space_type: SpaceType, space_id) -> Space:
    with session:
        metadata = FeedbackSpaceMetadata()
        space = Space(space_id=space_id, space_metadata=metadata,
                      space_type=space_type)
        session.add(space)
        await session.commit(space)
        return space


# async def get_or_create_space(session: AsyncSession, space_id, type: SpaceType) -> Space:
#     space = await get_space(session, space_id)
#     if not space:
#         return create_feedback_space()
