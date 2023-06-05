"""Authentication module.

Note: hash_password() function found in the user class module!
"""

import base64
import hashlib
import json
import os

import bcrypt
from fastapi_login import LoginManager

# from db import users

manager = LoginManager(secret=os.getenv("auth_secret_key"), token_url="/auth/token", use_cookie=True)


def verify_password(password: str, hashed_password: str) -> bool:
    if isinstance(password, str):
        password = password.encode()
    check_hash = base64.b64encode(hashlib.sha256(password).digest())
    return bcrypt.checkpw(check_hash, hashed_password.encode())


@manager.user_loader()
def load_user(user_query: str) -> json:
    # user = users.auth_search_user(user_query)
    user = None
    if user is None:
        return
    return user
