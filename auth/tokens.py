import time
from typing import Dict
import jwt

# FOR DEVELOPMENT USE ONLY
JWT_SECRET = "asdjqwee4yrhi8o234ry7fhikuhfgyuwiegbfeyiwkebvryuqgsbdhj@#!!#!$RDSIUEHOIJE"
JWT_ALGORITHM = "HS256"

# Constants measured in seconds
HOUR = 60 * 60
DAY = HOUR * 24

TOKEN_EXPIRATION = DAY


def create_token(
    user_id: str,
    username: str,
) -> Dict[str, str]:
    """Create a new token from the given token

    Args:
        token (str): token of the user.

    Returns:
        Dict[str,str]: A dictionary containing the token
    """
    contents = {
        "user_id": user_id,
        "expiration": int(time.time()) + TOKEN_EXPIRATION,
        "type": "soundsmith",
        "username": username,
    }
    token = jwt.encode(contents, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"jwt": token}


def create_spotify_token(
    spotify_token: str, expiration: int, scope: str
) -> Dict[str, str]:
    """Create a new token from the given token

    Args:
        token (str): token of the user.
        expiration (int): expiration of the token
        scope (str): scope of the token
    Returns:
        Dict[str,str]: A dictionary containing the token
    """
    contents = {
        "spotify_token": spotify_token,
        "expiration": expiration,
        "scope": scope,
        "type": "spotify",
    }
    token = jwt.encode(contents, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    """Decode a token.
    Args:
        token (str): The token to decode.

    Returns:
        dict: The decoded token.
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def validate_token(token: str) -> bool:
    """Validate a token and return True if it is valid and not expired.
    Args:
        token (str): The token to validate.

    Returns:
        bool: True if the token is valid and not expired, False otherwise.
    """
    try:
        jwt = decode_token(token)
        # if token is not expired, return true
        if jwt["expiration"] >= time.time():
            return True
        # if token is expired, return false
        return False
    except:
        return False
