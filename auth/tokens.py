import time
from typing import Dict
import jwt

# FOR DEVELOPMENT USE ONLY
JWT_SECRET = 'asdjqwee4yrhi8o234ry7fhikuhfgyuwiegbfeyiwkebvryuqgsbdhj@#!!#!$RDSIUEHOIJE'
JWT_ALGORITHM = 'HS256'

# Constants measured in seconds
HOUR = 60 * 60
DAY = HOUR * 24

TOKEN_EXPIRATION = DAY


def create_token(username: str) -> Dict[str, str]:
    """ Create a new token from the given username 

    Args:
        username (str): Username of the user.

    Returns:
        Dict[str,str]: A dictionary containing the token
    """
    contents = {
        'username': username,
        'expiration': int(time.time()) + DAY
    }
    token = jwt.encode(contents, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"jwt": token}


def decode_token(token: Dict[str, str]) -> dict:
    """ Decode a token.
    Args:
        token (Dict[str, str]): The token to decode.

    Returns:
        dict: The decoded token.
    """
    return jwt.decode(token['token'], JWT_SECRET, algorithms=[JWT_ALGORITHM])


def validate_token(token: Dict[str, str]) -> bool:
    """Validate a token and return True if it is valid and not expired.
    Args:
        token (Dict[str, str]): The token to validate.

    Returns:
        bool: True if the token is valid and not expired, False otherwise.
    """
    try:
        jwt = decode_token(token['token'])
        # if token is not expired, return true
        if jwt['expiration'] >= time.time():
            return True
        # if token is expired, return false
        return False
    except:
        return False
