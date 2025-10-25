from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, comment="Электронная почта"
    )
    hash_password: Mapped[str] = mapped_column(
        String(120), comment="Хэшированный пароль"
    )

    def __str__(self) -> str:
        return f"Пользователь №{self.id}"
