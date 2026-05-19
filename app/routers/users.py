from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.user import UserCreate

from app.repositories.user_repo import (
    UserRepository
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("")
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db)
):

    user = UserRepository.create(
        db,
        request.username,
        request.email,
        request.password
    )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }


@router.get("")
def get_users(
    db: Session = Depends(get_db)
):

    users = UserRepository.get_all(db)

    return users


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    UserRepository.delete(
        db,
        user_id
    )

    return {
        "message": "User deleted"
    }