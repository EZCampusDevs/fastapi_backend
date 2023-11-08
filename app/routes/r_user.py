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

"""User accounts API endpoint routes."""

from datetime import timedelta

from app import auth
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app import general_exceptions
from py_core.classes.user_classes import BasicUser, verify_password
from py_core.user import add_users

router = APIRouter(prefix="/user", tags=["user"])

# HTTPExceptions
API_200_EDITED_CRN_SCHEDULE = HTTPException(
    status_code=status.HTTP_200_OK, detail="Successfully edited your course schedule."
)
API_200_CREATED_USER = HTTPException(
    status_code=status.HTTP_200_OK,
    detail="Your account has been created! You'll be redirected shortly.",
)
API_200_EDITED_USER = HTTPException(
    status_code=status.HTTP_200_OK, detail="User details successfully changed."
)
API_200_VALIDATED_EXEC_USER = HTTPException(
    status_code=status.HTTP_200_OK, detail="User is of executive status or higher."
)
API_200_CHANGED_USER_PASSWORD = HTTPException(
    status_code=status.HTTP_200_OK, detail="Successfully changed your password."
)
API_200_DELETED_USER = HTTPException(
    status_code=status.HTTP_200_OK,
    detail="Your account has been deleted! You'll be redirected shortly.",
)
API_403_LOGIN_DENY = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")


def API_200_USER_LOGIN(login_data_dict: dict):
    return HTTPException(status_code=status.HTTP_200_OK, detail=login_data_dict)


def API_404_CRN_NOT_FOUND(invalid_crns: list[int]):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"CRNs: {invalid_crns} could not be found."
    )


@router.get("/info")
async def self_info(r: Request, user: BasicUser = Depends(auth.MANAGER)):
    """Get user info via username. LOGGING ENABLED.

    Args:
        r: fastapi.Request object.
        user: Logged-in user.
    """
    try:
        if user is None:
            raise general_exceptions.API_404_USER_NOT_FOUND

        # TODO (py_core issue #12): The following is a patch fix for fastapi_backend issue #14. The
        #  code below should be moved into a function in py_core's `user_classes.py`, something
        #  along the lines of `outbound_data(user: BasicUser)`.
        outbound_data_dict = {
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "description": user.description,
            "school_short_name": user.school_short_name,
            "program": user.program,
            "year_of_study": user.year_of_study,
            "is_private": user.is_private,
            "is_suspended": user.is_suspended,
            "account_status": user.account_status,
            "schedule_tag": user.schedule_tag,
            "created_at": user.created_at,
        }

    except HTTPException as h:
        # TODO: log
        raise h

    except Exception:  # All other python errors are cast and logged as 500.
        h = general_exceptions.API_500_ERROR
        # TODO: log
        raise h

    return outbound_data_dict


@router.post("/login")
async def login(r: Request, data: OAuth2PasswordRequestForm = Depends()):
    """User login. LOGGING ENABLED.

    Args:
        r: fastapi.Request object.
        data: Login request form data.
    """
    # try:
    user = auth.load_user(username=data.username)

    if user is None:
        raise general_exceptions.API_404_USER_NOT_FOUND

    if not verify_password(password=data.password, hashed_password=user.password):
        raise API_403_LOGIN_DENY

    access_token = auth.MANAGER.create_access_token(
        data={"sub": data.username}, expires=timedelta(days=1, seconds=0, microseconds=0)
    )

    # except HTTPException as h:
    #     # TODO: log
    #     raise h
    #
    # except Exception:  # All other python errors are cast and logged as 500.
    #     h = general_exceptions.API_500_ERROR
    #     # TODO: log
    #     raise h

    # TODO: log
    raise API_200_USER_LOGIN(
        {"access_token": access_token, "token_type": "bearer", "username": data.username}
    )


@router.post("/create")
async def user_new(r: Request, new_user: BasicUser):
    """Create new user account. LOGGING ENABLED.

    Args:
        r: fastapi.Request object.
        new_user: Logged-in user.
    """
    try:
        add_users([new_user])

    except HTTPException as h:
        # TODO: log
        raise h

    except Exception:  # All other python errors are cast and logged as 500.
        h = general_exceptions.API_500_ERROR
        # TODO: log
        raise h

    # TODO: log
    raise API_200_CREATED_USER


# @router.post("/edit")
# async def user_edit(r: Request, user: BasicUser = Depends(auth.manager)):
#     """Edit user's own account.
#
#     Args:
#         r: fastapi.Request object.
#         user: Logged-in user.
#     """
#     pass


# @router.post("/delete")
# async def user_delete(r: Request, user: BasicUser = Depends(auth.manager)):
#     """Delete user's own account.
#
#     Args:
#         r: fastapi.Request object.
#         user: Logged-in user.
#     """
#     pass
