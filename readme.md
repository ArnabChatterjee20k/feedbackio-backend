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
