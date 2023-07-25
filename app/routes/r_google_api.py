"""Google's API services API endpoint routes."""

import os

import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordBearer
from google_auth_oauthlib.flow import Flow
from typing import Annotated

# Extra Imports for Google Calendar thing
import json
import requests

load_dotenv()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = APIRouter(prefix="/google-api", tags=["google-api"])

# HTTPExceptions
API_200_AUTHORIZED_USER = HTTPException(status.HTTP_200_OK, "User is authenticated")
API_200_HEARTBEAT = HTTPException(status.HTTP_200_OK, "I am alive")
API_401_UNAUTHORIZED_USER = HTTPException(
    status.HTTP_401_UNAUTHORIZED, "Invalid or expired auth token"
)


@app.get("/")
async def heartbeat():
    return {"uwu": "uwu"}


# Assuming you've created a JWT token and set it as a bearer token in your requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/start")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar",
]

# Load your client_secrets.json
flow = Flow.from_client_secrets_file(
    client_secrets_file=os.getenv("google_client_credentials"),
    scopes=SCOPES,
    redirect_uri="http://localhost:8000/google-api/auth/callback",
)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, os.getenv("jwt_secret_key"), algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")


@router.get("/auth/start")
def start_auth():
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    return {"authorization_url": authorization_url}

@router.get("/auth/callback")
def auth_callback(code: str, state: str):
    flow.fetch_token(code=code)
    credentials = flow.credentials
    # Load credentials from the json.

    c_json = credentials.to_json()
    c_dict = json.loads(c_json)  # convert JSON string to dictionary

    # Prepare header for the request
    headers = {
        "Authorization": f'Bearer {c_dict["token"]}',  # use dictionary to get token
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Prepare the body for the event creation request
    event_body = {
        'summary': 'Example Event',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2023-07-28T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2023-07-28T17:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
    }

    # Make the request to create the event
    response = requests.post(
        'https://www.googleapis.com/calendar/v3/calendars/primary/events', 
        headers=headers,
        data=json.dumps(event_body)  # event data should be converted to JSON
    )

    if response.status_code == 200:
        print('Event created: %s' % (response.json().get('htmlLink')))
    else:
        print('Failed to create event:', response.content)

    return {"message": "success", "credentials": credentials.to_json()}



app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("fastapi_host"), port=int(os.getenv("fastapi_port")))