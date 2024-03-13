from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import Dict, List
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


@user_router.post(
    "/",
    response_description="Create a new user",
)
def create_new_user(user: User, request: Request) -> Dict:
    user = create_user(jsonable_encoder(user), request.app.database)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User could not be created",
        )
    user["_id"] = str(user["_id"])
    return user


@user_router.put(
    "/{user_id}",
    response_description="Update a user",
)
def update_user_by_id(user_id: str, user: UserUpdate, request: Request) -> None:
    user = update_user(user_id, request.app.database, username=user.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )


@user_router.delete(
    "/{username}",
    response_description="Delete a user",
)
def delete_user_by_username(username: str, request: Request) -> None:
    delete_user(username, request.app.database)
