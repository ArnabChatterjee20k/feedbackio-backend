# Installation
* Generating Requirements
```bash
    uv pip freeze > requirements.txt
```
* Installations
```bash
    uv pip install -r requirements.txt
```
# Migrations
1. Init
```shell
    alembic init <foldername>
```
2. Modify env.py and .ini files
3. Run the revision
```shell
alembic revision --autogenerate -m "initial commit"
```
4. Run upgrade/downgrade
```shell
alembic upgrade head
```
5. Check migration
```shell
alembic current
```
6. Checking history
```shell
alembic history --verbose
```
### How migration will work
https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-uptodate

> https://stackoverflow.com/questions/12409724/no-changes-detected-in-alembic-autogeneration-of-migrations-with-flask-sqlalchem

### Deployment
Here gunicorn is getting used for deployment on render
Generally these are followed
* Concurrency: More workers mean more requests can be handled simultaneously.
* CPU-bound Tasks: Set the number of workers to CPU cores * 2 + 1 for optimal CPU usage.
* I/O-bound Tasks: If the app spends time waiting for I/O (like API calls, DB queries), more workers can improve performance.

### Concurrency with fastapi and async
https://www.youtube.com/watch?v=1z8LLSZSWHM

### Async setup of sqlalchemy
https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308


### Concurrency issues of sqlalchemy shared sessions
https://readmedium.com/how-to-use-sqlalchemy-to-make-database-requests-asynchronously-e90a4c8c11b1

### Behaviour scalars in sqlalchemy
* If we select particular columns like this select(Model.id,Model.db) then .scalars().all() return the list of first col in the row that is Model.id.
So use .all() and it will return a Row() which is a tuple. Here we have to use indexing to get the data

* If we select the entire object select(Model) then .scalars().all() will give list of the Model and we directly extract properties by dot(.)

### supabase session pooler and transaction pooler
* session pooler -> serverful application
* transaction pooler -> serverless application
> Here session pooler will be used

### if using serverless and transaction pooling then prepared_statement_cache_size issue with pgbouncer(supabase uses it)
https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#prepared-statement-cache
https://github.com/sqlalchemy/sqlalchemy/issues/6467
* Have these changes
```
uri = postgresql+asyncpg://postgres:arnab@127.0.0.1:5432/medimyth?prepared_statement_cache_size=0
```
```python
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection, async_sessionmaker, create_async_engine
from sqlalchemy import NullPool
from fastapi import Depends
from typing import Annotated
from typing import AsyncIterator, Any
import contextlib
from sqlalchemy.orm import DeclarativeBase
import os

from uuid import uuid4

from asyncpg import Connection


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f'__asyncpg_{prefix}_{uuid4()}__'


class Base(DeclarativeBase):
    pass


class DBSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any]):
        self._engine = create_async_engine(host, connect_args={
                                           'statement_cache_size': 0, 'connection_class': CConnection}, **engine_kwargs)
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

```