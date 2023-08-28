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
def load_user(user_query: str) -> json:
    # user = users.auth_search_user(user_query)
    user = None
    if user is None:
        return
    return user
