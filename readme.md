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