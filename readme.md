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