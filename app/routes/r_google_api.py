"""Google's API services API endpoint routes."""

from fastapi import APIRouter, HTTPException, Request
from fastapi import status
from pydantic import BaseModel
from starlette.background import BackgroundTask

from app import general_exceptions
from app.google_services import authenticate_google, export_to_google_calendar
from py_core.classes.course_class import course_to_extended_meetings
from py_core.db.course import get_courses_via

router = APIRouter(prefix="/google-api", tags=["google-api"])


class RequestExportCourses(BaseModel):
    course_data_ids: list[int]
    creds: str | None = None
    calendar_name: str | None = None


@router.post("/auth")
async def auth(r: Request):
    try:
        detail = authenticate_google()
    except HTTPException as h:
        # TODO: LOG
        #  new_log(http_ref=h, request_model=r_model, request=r)  # Log error.
        raise h

    raise HTTPException(status_code=status.HTTP_200_OK, detail=detail)


@router.post("/gcal/export")
async def google_calendar_export(r: Request, r_model: RequestExportCourses):
    """Download ics file based on given course_data_ids.

    Args:
        r: fastapi.Request object.
        r_model: DownloadCourses request model object.

    Returns:
        Download for the created ics calendar file.
    """
    try:
        if not r_model.course_data_ids:
            raise general_exceptions.API_400_COURSE_DATA_IDS_UNSPECIFIED
        courses = get_courses_via(course_data_id_list=r_model.course_data_ids)
        if not courses:
            raise general_exceptions.API_404_COURSE_DATA_IDS_NOT_FOUND
        export_to_google_calendar(
            creds=r_model.creds, ex_mt_list=course_to_extended_meetings(courses),
            calendar_name=r_model.calendar_name
        )
    except HTTPException as h:
        # TODO: LOG
        #  new_log(http_ref=h, request_model=r_model, request=r)  # Log error.
        raise h
    # except Exception as e:  # All other python errors are cast and logged as 500.
    #     h = general_exceptions.API_500_ERROR
    #     # TODO: LOG
    #     #  new_log(http_ref=h, request_model=r_model, request=r)  # Log error.
    #     raise h
    # TODO: LOG
    #  new_log(http_ref=200, request_model=r_model, request=r)  # Log success.

    return HTTPException(
        status_code=status.HTTP_200_OK, detail="Successful export to Google Calendar.",
    )
