"""FastAPI main.py module.

Normally to run FastAPI manually using uvicorn you use: "uvicorn main:app --reload" in the terminal
from the directory of this file (main.py). However, here uvicorn is called so FastAPI should run
when main is run.

Remember to get to the docs it looks like this: http://localhost:8000/docs.
"""

import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path

    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.realpath(path))



import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from secrets import token_hex
from starlette.middleware.sessions import SessionMiddleware


#! Immediately Assert for Loaded .env (Before Importing routes)

load_dotenv_result = load_dotenv()

if not load_dotenv_result:
    raise Exception("Failed to load .env file!")

from app.general_exceptions import API_404_USER_NOT_FOUND
from app.routes import r_download_ics, r_experimental, r_google_api, r_schedule_optimizer
from auth import manager
from py_core import logging_util
from py_core.classes.user_classes import BasicUser
from py_core.db import init_database


# FastAPI app.
app = FastAPI()

# FastAPI middleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("session_secret_key"))

# FastAPI app routers:
app.include_router(r_download_ics.router)
app.include_router(r_experimental.router)
app.include_router(r_google_api.router)
app.include_router(r_schedule_optimizer.router)

# HTTPExceptions
API_200_AUTHORIZED_USER = HTTPException(status.HTTP_200_OK, "User is authenticated")
API_200_HEARTBEAT = HTTPException(status.HTTP_200_OK, "I am alive")
API_401_UNAUTHORIZED_USER = HTTPException(
    status.HTTP_401_UNAUTHORIZED, "Invalid or expired auth token"
)


@app.get("/")
async def heartbeat():
    raise API_200_HEARTBEAT


@app.get("/root")
async def root(user: BasicUser = Depends(manager)):
    if user is None:
        raise API_401_UNAUTHORIZED_USER
    raise API_200_AUTHORIZED_USER


@app.get("/session-id")
async def session_id(r: Request):
    """Generate session id based on SessionMiddleware JWT.

    Notes:
        Actual JWT created by SessionMiddleware at r.cookies["session"].
    """
    if "session_id" not in r.session:
        r.session["session_id"] = token_hex(16)  # You can adjust the length of the session ID.
    return {"session_id": r.session["session_id"]}


# FASTAPI \docs OAuth
# from datetime import timedelta
#
# from fastapi.security import OAuth2PasswordRequestForm
#
# from auth import load_user, verify_password
# from routes.r_user_accounts import API_403_LOGIN_DENY
#
#
# @app.post("/auth/token")  # FASTAPI \docs OAuth
# async def login(data: OAuth2PasswordRequestForm = Depends()):
#     username = data.username
#     password = data.password
#     user = load_user(username)
#     if user is None:
#         raise API_404_USER_NOT_FOUND
#     if not verify_password(password=password, hashed_password=user.hashed_password):
#         raise API_403_LOGIN_DENY
#     access_token = manager.create_access_token(data={"sub": username}, expires=timedelta(days=1))
#     return {"access_token": access_token, "token_type": "bearer", "username": username}


@app.get("/homepage")
async def homepage(user: BasicUser = Depends(manager)) -> dict:
    if user is None:
        raise API_404_USER_NOT_FOUND
    return {"valid": user.name}


if __name__ == "__main__":
    logging_util.setup_logging()
    logging_util.add_unhandled_exception_hook()
    init_database()
    uvicorn.run("main:app", host=os.getenv("fastapi_host"), port=int(os.getenv("fastapi_port")))
