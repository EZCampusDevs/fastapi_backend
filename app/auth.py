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

"""Authentication module.

Note: hash_password() function found in the user class module!
"""

import base64
import hashlib
import json
import os
import logging

import bcrypt
from fastapi_login import LoginManager
from py_core.user import get_users_via


_AUTH_SECRET_KEY_NAME = "AUTH_SECRET_KEY"

_secret = os.getenv(_AUTH_SECRET_KEY_NAME, None)

if _secret is None:
    msg = f"The '{_AUTH_SECRET_KEY_NAME}' environment variable does not exist"
    logging.error(msg)
    raise Exception(msg)

MANAGER: LoginManager = LoginManager(secret=_secret, token_url="/auth/token", use_cookie=True)


def verify_password(password: str, hashed_password: str) -> bool:
    if isinstance(password, str):
        password = password.encode()
    check_hash = base64.b64encode(hashlib.sha256(password).digest())
    return bcrypt.checkpw(check_hash, hashed_password.encode())


@MANAGER.user_loader()
def load_user(username: str) -> json:
    user = get_users_via(usernames=[username])[0]
    if user is None or not user:
        return
    return user
