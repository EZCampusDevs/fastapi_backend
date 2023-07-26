"""Google's API services API endpoint routes."""

import json
import logging
import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter
from google_auth_oauthlib.flow import Flow

logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter(prefix="/google-api", tags=["google-api"])

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar",
]

# Load your client_secrets.json.
flow = Flow.from_client_secrets_file(
    client_secrets_file=os.getenv("google_client_credentials"),
    scopes=SCOPES,
    redirect_uri="http://localhost:8000/google-api/auth/callback",
)


@router.get("/auth/start")
def start_auth():
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    return {"authorization_url": authorization_url}


@router.get("/auth/callback")
def auth_callback(code: str, state: str):
    """Google OAuth2 Callback for Calendar Event exporting"""
    flow.fetch_token(code=code)
    credentials = flow.credentials  # Load credentials from the json.

    c_json = credentials.to_json()
    c_dict = json.loads(c_json)  # Convert JSON string to dictionary.

    # Prepare header for the request.
    headers = {
        "Authorization": f'Bearer {c_dict["token"]}',
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Prepare the body for the event creation request.
    event_body = {
        "summary": "Example Event",
        "location": "800 Howard St., San Francisco, CA 94103",
        "description": "A chance to hear more about Google's developer products.",
        "start": {
            "dateTime": "2023-07-28T09:00:00-07:00",
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "dateTime": "2023-07-28T17:00:00-07:00",
            "timeZone": "America/Los_Angeles",
        },
    }

    # Make the request to create the event.
    response = requests.post(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers=headers,
        data=json.dumps(event_body),  # Event data should be converted to JSON.
    )

    if response.status_code == 200:
        logging.debug(
            f"Successfully created Google Calendar event: {(response.json().get('htmlLink'))}"
        )
    else:
        logging.error(f"Failed to create Google Calendar event: {response.content}")
    return {"message": "success", "credentials": credentials.to_json()}
