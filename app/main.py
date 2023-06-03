"""FastAPI main.py module.

Normally to run FastAPI manually using uvicorn you use: "uvicorn main:app --reload" in the terminal from the directory
of this file (main.py). However, here uvicorn is called so FastAPI should run when main is run.

Remember to get to the docs it looks like this: http://localhost:8000/docs.
"""

import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.general_exceptions import API_404_USER_NOT_FOUND
from app.routes import (r_download_ics)
from auth import manager
from py_core.classes.user_classes import BasicUser

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("origins_domain")], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

# FastAPI app routers:
app.include_router(r_download_ics.router)

# HTTPExceptions
API_200_AUTHORIZED_USER = HTTPException(status.HTTP_200_OK, "User is authenticated")
API_200_UNAUTHORIZED_USER = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired auth token")


@app.get("/")
async def root(user: BasicUser = Depends(manager)):
    if user is None:
        raise API_200_UNAUTHORIZED_USER
    raise API_200_AUTHORIZED_USER


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
    uvicorn.run("main:app", host=os.getenv("fastapi_host"), port=int(os.getenv("fastapi_port")))