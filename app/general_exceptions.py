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

"""General FastAPI HTTPExceptions

Typically, HTTPExceptions are written in to each individual router module. All HTTPExceptions in
this module are called from more than on router and/or called from one or more non-router
module(s). This module works to prevent circular imports and consolidate HTTPExceptions that are
called from outside the routers package.

Common modules calling these exceptions:
- DB modules.
- Router modules.
- main.py.
"""

from fastapi import HTTPException, status

API_400_COURSE_DATA_IDS_UNSPECIFIED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="course_data_ids not specified."
)
API_400_COURSE_IDS_UNSPECIFIED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="course_codes not specified."
)
API_404_USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't exist."
)
API_404_COURSE_DATA_IDS_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="course_data_ids not found."
)
API_404_COURSE_IDS_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="course_ids not found."
)
API_404_COURSES_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="course_ids not found."
)
API_500_ERROR = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal server error. The issue has been logged and will be reviewed by the "
    "development team. Please contact support if you require an urgent response.",
)
API_200_AUTHORIZED_USER = HTTPException(status.HTTP_200_OK, "User is authenticated")
API_200_HEARTBEAT = HTTPException(
    status.HTTP_200_OK,
    (
        "EZCampus FastAPI Backend: Online"
        "License: https://www.gnu.org/licenses/agpl-3.0.html"
        "Source: https://github.com/EZCampusDevs/fastapi_backend/"
    ),
)
API_401_UNAUTHORIZED_USER = HTTPException(
    status.HTTP_401_UNAUTHORIZED, "Invalid or expired auth token"
)
