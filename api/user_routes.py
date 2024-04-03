from datetime import datetime
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import Dict
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from auth import hasher, tokens
from database.crud import (
    get_hashed_password,
    get_user,
    create_user,
    update_user,
    delete_user,
)

from api.models import CreateUser, User, UserUpdate

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
def create_new_user(user: CreateUser, request: Request) -> Dict[str, str]:
    user = create_user(user.username, user.password, request.app.database)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User could not be created",
        )
    return {"user_id": str(user)}


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


@user_router.post("/auth", response_description="Get Login Token")
def get_token(user: CreateUser, request: Request, response: Response):
    password = get_hashed_password(user.username, request.app.database)
    validCredentials = hasher.verify_password(user.password, password)
    if validCredentials:
        token = tokens.create_token(
            get_user(user.username, request.app.database)["_id"], user.username
        )
        return token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
    )
