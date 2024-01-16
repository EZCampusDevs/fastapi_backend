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

"""Student Availability Heatmap download API endpoint routes."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, root_validator, validator
from starlette.background import BackgroundTask
from datetime import date

from app import general_exceptions
from app.cache_path_manipulation import remove_file_path
from app.student_availability import generate_heatmap
from py_core.course import get_courses_via, get_course_ids
from py_core.logging_util import log_endpoint

router = APIRouter(prefix="/heatmap", tags=["heatmap"])


class RequestDownloadHeatmap(BaseModel):
    course_data_ids: list[int] = []
    course_ids: list[int] = []
    course_codes: list[str] = []
    term_id: int | None = None  # Only required of course_codes are specified, checked by validator.
    scope_date_start: date
    scope_date_end: date
    scope_hour_start: int = 8
    scope_hour_end: int = 20

    @root_validator()
    def verify_term_id(cls, values):
        course_codes = values.get("course_codes")
        term_id = values.get("term_id")
        if not course_codes and term_id is not None:
            values["term_id"] = None
        else:
            if course_codes and term_id is None:
                raise ValueError(f"If course_codes are specified, term_id must also be specified")
        return values

    @validator("scope_hour_start")
    def verify_scope_hour_start(cls, v):
        if not (0 <= v <= 23):
            raise ValueError(f"Expected 0 <= scope_hour_start={v} <= 23")
        return v

    @validator("scope_hour_end")
    def verify_scope_hour_end(cls, v):
        if not (0 <= v <= 23):
            raise ValueError(f"Expected 0 <= scope_hour_end={v} <= 23")
        return v

    @root_validator()
    def verify_scope_dates(cls, values):
        scope_date_start = values.get("scope_date_start")
        scope_date_end = values.get("scope_date_end")
        if not (scope_date_start <= scope_date_end):
            raise ValueError(
                f"Expected scope_date_start={scope_date_start} <= scope_date_end={scope_date_end}"
            )
        return values

    @root_validator()
    def verify_scope_hours(cls, values):
        scope_hour_start = values.get("scope_hour_start")
        scope_hour_end = values.get("scope_hour_end")
        if not (scope_hour_start < scope_hour_end):
            raise ValueError(
                f"Expected scope_hour_start={scope_hour_start} < scope_hour_end={scope_hour_end}"
            )
        return values


@router.post("/csv")
async def download_csv_heatmap(r: Request, r_model: RequestDownloadHeatmap) -> FileResponse:
    """Download student availability heatmap as csv file format.

    Args:
        r: fastapi.Request object.
        r_model: RequestHeatmap request model object.

    Returns:
        FileResponse.
    """
    try:
        if not r_model.course_data_ids and not r_model.course_ids and not r_model.course_codes:
            raise general_exceptions.API_400_COURSE_DATA_IDS_UNSPECIFIED

        course_ids = get_course_ids(course_codes=r_model.course_codes, term_id=r_model.term_id)
        course_ids.extend(r_model.course_ids)

        courses = get_courses_via(
            course_data_id_list=r_model.course_data_ids, course_id_list=list(set(course_ids))
        )

        if not courses:
            raise general_exceptions.API_404_COURSE_DATA_IDS_NOT_FOUND

        csv_file_path = generate_heatmap(
            source_list=courses,
            scope_date_start=r_model.scope_date_start,
            scope_date_end=r_model.scope_date_end,
            scope_hour_start=r_model.scope_hour_start,
            scope_hour_end=r_model.scope_hour_end,
            save_as_csv=True,  # Save as csv file format.
        )[
            "csv"
        ]  # Get generated csv file path format.
    except HTTPException as h:
        log_endpoint(h, r, f"detail={h.detail} r_model={r_model}")
        raise h
    except Exception as e:  # All other python errors are cast and logged as 500.
        h = general_exceptions.API_500_ERROR
        log_endpoint(h, r, f"detail={h.detail} e={e} r_model={r_model}")
        raise h

    h = FileResponse(
        status_code=200,
        path=csv_file_path,
        # csv file type.
        filename=f"ezc_heatmap_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv",
        # MIME for csv.
        media_type="text/csv",
        background=BackgroundTask(remove_file_path, csv_file_path),
    )
    log_endpoint(h, r, f"r_model={r_model}")
    return h


@router.post("/xlsx")
async def download_xlsx_heatmap(r: Request, r_model: RequestDownloadHeatmap) -> FileResponse:
    """Download student availability heatmap as xlsx file format.

    Args:
        r: fastapi.Request object.
        r_model: RequestHeatmap request model object.

    Returns:
        FileResponse.
    """
    try:
        if not r_model.course_data_ids and not r_model.course_ids and not r_model.course_codes:
            raise general_exceptions.API_400_COURSE_DATA_IDS_UNSPECIFIED

        course_ids = get_course_ids(course_codes=r_model.course_codes, term_id=r_model.term_id)
        course_ids.extend(r_model.course_ids)

        courses = get_courses_via(
            course_data_id_list=r_model.course_data_ids, course_id_list=list(set(course_ids))
        )

        if not courses:
            raise general_exceptions.API_404_COURSE_DATA_IDS_NOT_FOUND

        xlsx_file_path = generate_heatmap(
            source_list=courses,
            scope_date_start=r_model.scope_date_start,
            scope_date_end=r_model.scope_date_end,
            scope_hour_start=r_model.scope_hour_start,
            scope_hour_end=r_model.scope_hour_end,
            save_as_xlsx=True,  # Save as xlsx file format.
        )[
            "xlsx"
        ]  # Get generated xlsx file path format.
    except HTTPException as h:
        log_endpoint(h, r, f"detail={h.detail} r_model={r_model}")
        raise h
    except Exception as e:  # All other python errors are cast and logged as 500.
        h = general_exceptions.API_500_ERROR
        log_endpoint(h, r, f"detail={h.detail} e={e} r_model={r_model}")
        raise h

    h = FileResponse(
        status_code=200,
        path=xlsx_file_path,
        # xlsx file type.
        filename=f"ezc_heatmap_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.xlsx",
        # MIME for xlsc.
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        background=BackgroundTask(remove_file_path, xlsx_file_path),
    )
    log_endpoint(h, r, f"r_model={r_model}")
    return h
