from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection, async_sessionmaker, create_async_engine
from fastapi import Depends
from typing import Annotated
from typing import AsyncIterator, Any
import contextlib
from sqlalchemy.orm import DeclarativeBase
import os


class Base(DeclarativeBase):
    pass


class DBSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any]):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncConnection]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.rollback()


database_url = os.environ.get("ASYNC_DB_URL")
sessionmanager = DBSessionManager(database_url, {"echo": False})


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
