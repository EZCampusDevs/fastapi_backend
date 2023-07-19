"""
Google API Services.

Used as a means of expanding EZCampus's support for 3rd party software.
"""

import re
import os
import pickle
from datetime import datetime
import pytz

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from py_core.classes.extended_meeting_class import ExtendedMeeting

load_dotenv()

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar",
]


def authenticate_google(creds: str | Credentials | None = None) -> None | Credentials:
    """Google OAuth 2.0 authentication page and user credentials storage.

    Returns:
        None if user credentials exist local, else google.oauth2.credentials.Credentials.
    """
    # if os.path.exists("token.pickle"):
    #     with open("token.pickle", "rb") as token:
    #         creds = pickle.load(token)
    if isinstance(creds, str):
        creds = pickle.loads(creds)
    if creds is None or not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("google_client_credentials"), SCOPES
            )
            creds = flow.run_local_server(port=int(os.getenv("google_auth_flow_port")))
        # with open("token.pickle", "wb") as token:
        #     pickle.dump(creds, token)
    return creds


def __get_or_create_calendar(service: Resource, calendar_name: str):
    calendar_list_entry = service.calendarList().get(calendarId="primary").execute()
    if "items" in calendar_list_entry:
        for calendar_list_entry in calendar_list_entry["items"]:
            if calendar_list_entry["summary"] == calendar_name:
                return calendar_list_entry["id"]
    # Create calendar if it doesn't exist
    calendar = {"summary": calendar_name, "timeZone": "America/Los_Angeles"}
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar["id"]


def __create_event(service, calendar_id: str, ex_mt: ExtendedMeeting):
    event = {
        "summary": ex_mt.name,
        "location": ex_mt.location,
        "description": ex_mt.description,
        "start": {
            "dateTime": ex_mt.dt_start().isoformat(),
            "timeZone": "America/Toronto",
        },
        "end": {
            "dateTime": ex_mt.dt_end().isoformat(),
            "timeZone": "America/Toronto",
        },
        "recurrence": [],
    }
    if ex_mt.occurrence_unit is not None:
        full_rrule_str = str(ex_mt.get_rrule())
        recurrence = full_rrule_str[full_rrule_str.index("RRULE:") :]

        # RRULE UNTIL requires UTC with the trailing "Z" character.
        # If the UNTIL datetime is not timezone-aware, add timezone information.
        until_date = ex_mt.get_rrule()._until
        if until_date.tzinfo is None or until_date.tzinfo.utcoffset(until_date) is None:
            # Assume the original timezone is America/Toronto.
            until_date = pytz.timezone("America/Toronto").localize(until_date)
        utc_until_date = until_date.astimezone(pytz.utc)  # Convert to UTC.

        # Update to new until value.
        recurrence = re.sub(
            r"(?<=UNTIL=)[^;]+", utc_until_date.strftime("%Y%m%dT%H%M%SZ"), recurrence
        )

        event["recurrence"].append(recurrence)

    return service.events().insert(calendarId=calendar_id, body=event).execute()


def export_to_google_calendar(
    ex_mt_list: list[ExtendedMeeting],
    creds: str | Credentials | None = None,
    calendar_name: str | None = None,
):
    if creds is None:
        creds = authenticate_google(creds)

    service = build("calendar", "v3", credentials=creds)

    time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not (isinstance(calendar_name, str) and len(calendar_name) > 0):
        calendar_name = f"EZCampus ({time_string})"
    calendar_id = __get_or_create_calendar(service, calendar_name)

    for ex_mt in ex_mt_list:
        __create_event(service=service, calendar_id=calendar_id, ex_mt=ex_mt)
