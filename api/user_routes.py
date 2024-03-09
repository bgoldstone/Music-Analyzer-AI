from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from database.crud import get_user, create_user, update_user, delete_user

from models import User, UserUpdate

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get(
    "/{username}",
    response_description="Get a single user",
)
def get_user_by_username(username: str, request: Request):
    user = get_user(username, request.app.database)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {username} not found",
        )
    user["_id"] = str(user["_id"])
    return user
