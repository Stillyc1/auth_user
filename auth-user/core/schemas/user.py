import re

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from core.schemas.base_user import UserBase


class UserCreate(UserBase):
    """Схема создания пользователя."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    password_2: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError(
                "Пароль должен содержать минимум 8 символов, буквы и цифры"
            )
        return v

    @field_validator("password_2")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Некорректный email")
        return v


class UserRead(UserBase):
    """Схема отображения пользователя."""

    id: int
    email: EmailStr


class TokenRequest(UserBase):
    """Схема запроса на вход"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема ответа на вход."""

    access: str
    token_type: str


class LogoutResponse(BaseModel):
    """Схема ответа на выход."""

    detail: str
