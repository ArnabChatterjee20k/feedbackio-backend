import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from api import create_api
from app.analytics import analytics_router
import time


async def is_valid_request(request: Request):
    if bool(os.environ.get("PROD")!="1"):
        return True
    token = request.headers.get("X-FEEDBACK-AUTH-TOKEN")
    print(token, os.environ.get("X-FEEDBACK-AUTH-TOKEN"))

    if not token:
        return False  # Return False if no token is provided

    is_valid = token == os.environ.get("X-FEEDBACK-AUTH-TOKEN")
    print(is_valid)

    return is_valid


def create_app():
    app = FastAPI()

    # # Configure CORS for FastAPI
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost",
                       "http://127.0.0.1", os.environ.get("APP_URL")],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # # Create and mount the Flask app
    flask_app = create_api()

    # Middleware for request validation
    @app.middleware("http")
    async def check_validity(request: Request, call_next):
        endpoint = request.url.path
        if endpoint == "/":
            return await call_next(request)

        if not await is_valid_request(request):
            return JSONResponse(
                status_code=403,
                content={"message": "Forbidden"}
            )

        return await call_next(request)
    # include the fast api first
    app.include_router(router=analytics_router,prefix="/analytics")
    app.mount("/", WSGIMiddleware(flask_app))
    return app