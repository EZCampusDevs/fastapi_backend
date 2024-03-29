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

"""Schedule optimizer API endpoint routes."""

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app import general_exceptions
from app.schedule_optimizer import course_level_optimizer
from py_core.classes.extended_meeting_class import http_format
from py_core.classes.optimizer_criteria_class import CourseOptimizerCriteria
from py_core.course import get_courses_via
from py_core.logging_util import log_endpoint

router = APIRouter(prefix="/optimizer", tags=["optimizer"])


class RequestScheduleOptimizer(BaseModel):
    """Request body for optimizer endpoint.

    course_codes: List of course ids required for schedule (to optimize for).
    optimizer_criteria: Optimizer criteria in a json string.
    required_crns: List of CRNs required in the schedule or None.
    ensure_open_seats: Optional condition, if ensure_open_seats is True, schedule will only build
        if courses have a minimum of 1 seat open, default is False.
    ensure_restrictions_met: Optional condition, if ensure_restrictions_met is True, schedule will
        only build if courses have all their restrictions met, default is False.
    restrictions_met: Optional condition, Dictionary of course restrictions met by the user.
    """

    course_ids: list[int] = []
    required_course_data_ids: list[int] = []
    optimizer_criteria: CourseOptimizerCriteria
    ensure_open_seats: bool = True
    ensure_restrictions_met: bool = False
    restrictions_met: dict = None


class RequestRestrictions(BaseModel):
    """Request body for restrictions endpoint.

    config_name: Config name.
    course_codes: List of course codes to get all (merged) restrictions of.
    """

    config_name: str
    course_codes: list[str]


@router.post("/schedule")
async def schedule_optimizer(r: Request, r_model: RequestScheduleOptimizer):
    """Download ics file based on given course_data_ids.

    Args:
        r: fastapi.Request object.
        r_model: DownloadCourses request model object.

    Returns:
        Download for the created ics calendar file.
    """
    try:
        # Process course_ids.
        if not r_model.course_ids:
            raise general_exceptions.API_400_COURSE_IDS_UNSPECIFIED
        courses = get_courses_via(course_id_list=r_model.course_ids)
        if not courses:
            raise general_exceptions.API_404_COURSE_IDS_NOT_FOUND
        # Process required course_data_ids.
        required_courses = get_courses_via(course_data_id_list=r_model.required_course_data_ids)
        if r_model.required_course_data_ids and not required_courses:
            raise general_exceptions.API_404_COURSE_DATA_IDS_NOT_FOUND
        # Optimize.
        result = course_level_optimizer(
            options=courses,
            criteria=r_model.optimizer_criteria,
            required_courses=required_courses,
            ensure_open_seats=r_model.ensure_open_seats,
            ensure_restrictions_met=r_model.ensure_restrictions_met,
            restrictions_met=r_model.restrictions_met,
        )
        result["schedule"] = http_format(result["schedule"])  # Convert for HTTP safe raise.
    except HTTPException as h:
        log_endpoint(h, r, f"detail={h.detail} r_model={r_model}")
        raise h
    except Exception as e:  # All other python errors are cast and logged as 500.
        h = general_exceptions.API_500_ERROR
        log_endpoint(h, r, f"detail={h.detail} e={e} r_model={r_model}")
        raise h
    h = HTTPException(status_code=status.HTTP_200_OK, detail=result)
    log_endpoint(h, r, f"r_model={r_model}")
    raise h
