"""ICS download API endpoint routes."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from app import general_exceptions
from app.cache_path_manipulation import remove_file_path
from app.ics_manipulation import create_ics_calendar
from py_core.db.course import get_courses_via

router = APIRouter(prefix="/download", tags=["download"])


class RequestDownloadCourses(BaseModel):
    course_data_ids: list[int]


@router.post("/ics/courses")
async def courses_download(r: Request, r_model: RequestDownloadCourses) -> FileResponse:
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
        file_path = create_ics_calendar(source_list=courses)
    except HTTPException as h:
        # TODO: LOG
        #  new_log(http_ref=h, request_model=r_model, request=r)  # Log error.
        raise h
    except Exception as e:  # All other python errors are cast and logged as 500.
        h = general_exceptions.API_500_ERROR
        print(e)
        #  new_log(http_ref=h, request_model=r_model, request=r)  # Log error.
        raise h
    # TODO: LOG
    #  new_log(http_ref=200, request_model=r_model, request=r)  # Log success.

    return FileResponse(
        status_code=200,
        path=file_path,
        filename=f"courses_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.ics",
        media_type="text/calendar",
        background=BackgroundTask(remove_file_path, file_path),
    )
