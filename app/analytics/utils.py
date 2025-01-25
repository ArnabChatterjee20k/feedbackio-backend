from .schema import PageType, PageVisitSchema, FeedbackSpaceMetadata, SpaceType
from .model import PageVisit
from sqlalchemy.ext.asyncio import AsyncSession
from .model import PageVisit, Space
from sqlalchemy import select


async def create_page_visit(session: AsyncSession, payload: PageVisitSchema):
    visit = PageVisit(**payload)
    session.add(visit)


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