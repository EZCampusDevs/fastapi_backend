"""Google's API services API endpoint routes."""

import json
import logging
import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, status
from google_auth_oauthlib.flow import Flow
from pydantic import BaseModel
from py_core.db.course import get_courses_via
from app import general_exceptions
from app.gcal_json_manipulation import get_gcal_event_jsons

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
    redirect_uri="http://localhost:3000/google-auth-callback",
)


@router.get("/auth/start")
def start_auth():
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    return {"authorization_url": authorization_url}


class RequestGCalExport(BaseModel):
    code: str
    course_data_ids: list[int]


@router.post("/auth/callback")
def auth_callback(r: Request, r_model: RequestGCalExport):
    """Google OAuth2 Callback for Calendar Event exporting"""
    flow.fetch_token(code=r_model.code)
    credentials = flow.credentials  # Load credentials from the json.

    c_json = credentials.to_json()
    c_dict = json.loads(c_json)  # Convert JSON string to dictionary.

    if not r_model.course_data_ids:
        raise general_exceptions.API_400_COURSE_DATA_IDS_UNSPECIFIED
    courses = get_courses_via(course_data_id_list=r_model.course_data_ids)
    if not courses:
        raise general_exceptions.API_404_COURSE_DATA_IDS_NOT_FOUND

    # Prepare header for the request.
    headers = {
        "Authorization": f'Bearer {c_dict["token"]}',
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    json_str_event_bodies = get_gcal_event_jsons(courses)

    # Prepare the body for the event creation request.
    for body in json_str_event_bodies:
        # Make the request to create the event(s).
        response = requests.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers=headers,
            data=body,
        )

        if response.status_code == status.HTTP_200_OK:
            logging.debug(
                f"Successfully created Google Calendar event: {(response.json().get('htmlLink'))}"
            )
            logging.debug(
                f"Successfully created Google Calendar event(s): {r_model.course_data_ids}"
            )
        else:
            logging.error(f"Failed to create Google Calendar event(s): {response.content}")

    return {"message": "completed"}  # , "credentials": credentials.to_json()}
