from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User, db_helper
from core.redis import redis
from core.schemas.user import (LogoutResponse, TokenRequest, TokenResponse,
                               UserCreate)

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = settings.jwt.secret_key
ALGORITHM = settings.jwt.algorithm
ACCESS_TOKEN = settings.jwt.access_token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login/")


class UserService:
    async def create_user(
        self,
        session: AsyncSession,
        user_create: UserCreate,
    ) -> User:
        # Проверяем, существует ли пользователь с таким email
        existing_user_query = await session.execute(
            select(User).filter(User.email == user_create.email)
        )
        existing_user = existing_user_query.scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email уже существует.")

        hash_password = self.set_password(user_create.password)
        user = User(email=user_create.email, hash_password=hash_password)
        session.add(user)

        try:
            await session.commit()
            await session.refresh(user)
            return user
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=500, detail="Ошибка передачи данных.")

    async def login_user(
        self, session: AsyncSession, form_data: TokenRequest
    ) -> TokenResponse:
        user = await self.get_user(session, str(form_data.email))
        if not user or not self.check_password(
            form_data.password, str(user.hash_password)
        ):
            raise HTTPException(
                status_code=400,
                detail="Неправильное имя пользователя или пароль!",
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.email, "at": ACCESS_TOKEN},
            expires_delta=access_token_expires,
        )
        return TokenResponse(access=access_token, token_type="bearer")

    async def get_current_user(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"Authorization": "Bearer"},
        )

        try:
            is_revoked = await redis.get(token)
            if is_revoked:
                raise credentials_exception

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            at = payload.get("at")

            if not all([email, at]):
                raise credentials_exception

            if at == ACCESS_TOKEN:
                return await self.get_user(session=session, email=email)

        except JWTError:
            raise credentials_exception

        raise credentials_exception

    @staticmethod
    async def logout_user(token: str) -> LogoutResponse:
        """
        Добавляет токен в Redis (черный список), если это access token.
        Возвращает подтверждение успешного выхода.
        """
        try:
            # Проверяем, не находится ли токен уже в черном списке
            is_revoked = await redis.get(token)
            if is_revoked:
                raise HTTPException(status_code=422, detail="Вы уже вышли из системы.")

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            at: str = payload.get("at")

            if at != ACCESS_TOKEN:
                raise HTTPException(status_code=422, detail="Не существующий токен.")

            expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
            await redis.set(token, "revoked", ex=expire_minutes * 60)

            return LogoutResponse(detail="Вы успешно вышли из системы.")

        except JWTError as e:
            raise HTTPException(
                status_code=401, detail="Недействительный токен."
            ) from e

    @staticmethod
    async def get_user(session: AsyncSession, email: str) -> User | None:
        result = await session.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def set_password(
        raw_password: str,
    ) -> str:
        """Функция для хеширования пароля."""
        return pwd_context.hash(raw_password)

    @staticmethod
    def check_password(
        raw_password: str,
        hash_password: str,
    ) -> bool:
        """Функция для проверки пароля."""
        return pwd_context.verify(raw_password, hash_password)
