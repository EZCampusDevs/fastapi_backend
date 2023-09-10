# Copyright (C) 2022-2023 EZCampus 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""ICS download API endpoint routes."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from app import general_exceptions
from app.cache_path_manipulation import remove_file_path
from app.export.ics_manipulation import create_ics_calendar
from app.export.notion_csv_manipulation import create_notion_csv
from py_core.db.course import get_courses_via
from py_core.logging_util import log_endpoint

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
        log_endpoint(h, r, f"detail={h.detail} r_model={r_model}")
        raise h
    except Exception as e:  # All other python errors are cast and logged as 500.
        h = general_exceptions.API_500_ERROR
        log_endpoint(h, r, f"detail={h.detail} e={e} r_model={r_model}")
        raise h

    h = FileResponse(
        status_code=200,
        path=file_path,
        filename=f"courses_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.ics",
        media_type="text/calendar",
        background=BackgroundTask(remove_file_path, file_path),
    )
    log_endpoint(h, r, f"r_model={r_model}")
    return h


@router.post("/csv/courses")
async def notion_courses_download(r: Request, r_model: RequestDownloadCourses) -> FileResponse:
    """Download Notion csv file based on given course_data_ids.

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
        file_path = create_notion_csv(source_list=courses)
    except HTTPException as h:
        log_endpoint(h, r, f"detail={h.detail} r_model={r_model}")
        raise h
    except Exception as e:  # All other python errors are cast and logged as 500.
        h = general_exceptions.API_500_ERROR
        log_endpoint(h, r, f"detail={h.detail} e={e} r_model={r_model}")
        raise h

    h = FileResponse(
        status_code=200,
        path=file_path,
        filename=f"courses_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv",
        media_type="text/csv",
        background=BackgroundTask(remove_file_path, file_path),
    )
    log_endpoint(h, r, f"r_model={r_model}")
    return h
