from fastapi import APIRouter
analytics_router = APIRouter(tags=["analytics"])
from . import model
from . import routes