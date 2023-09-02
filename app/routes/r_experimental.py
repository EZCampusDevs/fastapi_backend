""""ICS download API endpoint routes."""

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app import general_exceptions
from py_core.classes.course_class import course_to_extended_meetings
from py_core.db.course import get_courses_via
from py_core.classes.extended_meeting_class import http_format

router = APIRouter(prefix="/experimental", tags=["experimental"])


class RequestEvents(BaseModel):
    course_data_ids: list[int] = []
    course_ids: list[int] = []


@router.post("/events")
async def events_example(r: Request, r_model: RequestEvents):
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
        ex_mts = course_to_extended_meetings(
            get_courses_via(
                course_data_id_list=r_model.course_data_ids,
                course_id_list=r_model.course_ids,
            )
        )
    except HTTPException as h:
        # TODO: LOG
        #  new_log(http_ref=h, request_model=r_model, request=r)  # Log error.
        raise h
    except Exception as e:  # All other python errors are cast and logged as 500.
        print(e)
        h = general_exceptions.API_500_ERROR
        # TODO: LOG
        #  new_log(http_ref=h, request_model=r_model, request=r)  # Log error.
        raise h
    # TODO: LOG
    #  new_log(http_ref=200, request_model=r_model, request=r)  # Log success.

    return HTTPException(status.HTTP_200_OK, http_format(ex_mts))
