from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.user_service import UserService
from core.config import settings
from core.models import User, db_helper
from core.schemas.user import (LogoutResponse, TokenRequest, TokenResponse,
                               UserCreate, UserRead)

router = APIRouter(
    prefix=settings.api.users,
    tags=["Users"],
)


@router.post(
    "/register/",
    response_model=UserRead,
)
async def create_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_service: Annotated[UserService, Depends()],
    user: UserCreate,
) -> User:
    """Создание пользователя."""
    user_ = await user_service.create_user(session=session, user_create=user)
    return user_


@router.post(
    "/login/",
)
async def login(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_service: Annotated[UserService, Depends()],
    form_data: TokenRequest,
) -> TokenResponse:
    """Вход пользователя."""
    return await user_service.login_user(session=session, form_data=form_data)


@router.get(
    "/me/",
    response_model=UserRead,
)
async def get_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_service: Annotated[UserService, Depends()],
    token: str,
) -> User:
    """Получаем информацию о пользователе."""
    return await user_service.get_current_user(session=session, token=token)


@router.post("/logout/", response_model=LogoutResponse)
async def logout(
    user_service: Annotated[UserService, Depends()],
    token: str,
) -> LogoutResponse:
    """Выход пользователя."""
    return await user_service.logout_user(token=token)
