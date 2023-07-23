"""Google's API services API endpoint routes."""

import os

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordBearer
from google_auth_oauthlib.flow import Flow
from typing import Annotated

load_dotenv()

router = APIRouter(prefix="/google-api", tags=["google-api"])

# Assuming you've created a JWT token and set it as a bearer token in your requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/start")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar",
]

# Load your client_secrets.json
flow = Flow.from_client_secrets_file(
    client_secrets_file=os.getenv("google_client_credentials"),
    scopes=SCOPES,
    redirect_uri="http://localhost:8000/google-api/auth/callback",
)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, os.getenv("jwt_secret_key"), algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")


@router.get("/auth/start")
def start_auth():
    payload = {}
    
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    # Store the state in your JWT session or any other way you handle user session.
    # Add logic here to add the state to your session.
    payload["state"] = state

    # Create a new JWT with the state included.
    new_token = jwt.encode(payload, os.getenv("jwt_secret_key"), algorithm="HS256")
    print(authorization_url)

    return {"authorization_url": authorization_url, "token": new_token}


@router.get("/auth/callback")
def auth_callback(code: str, state: str, token: Annotated[str, Depends(oauth2_scheme)]):
    """Callback for user credentials using JWT.

    Args:
        code: Authorization code that Google's OAuth 2.0 server returns as part of OAuth 2.0
            authorization code flow.
        state: OAuth 2.0 authorization parameter.
            See: https://auth0.com/docs/secure/attack-protection/state-parameters.
        token: JWT token.
    """
    # Verify the JWT and get the payload.
    payload = verify_token(token)
    print(payload)

    # Retrieve the stored state.
    stored_state = payload.get("state", None)
    if stored_state != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State mismatch error")
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Store the credentials in your session or database.
    payload["credentials"] = credentials.to_json()

    # Create a new JWT with the credentials included.
    new_token = jwt.encode(payload, os.getenv("jwt_secret_key"), algorithm="HS256")

    return {"message": "success", "token": new_token}
