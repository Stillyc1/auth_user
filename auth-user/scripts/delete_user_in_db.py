import asyncio
import sys
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(str(Path(__file__).parent.parent))

from core.models.db_helper import db_helper
from core.models.user import User


async def delete_all_users(session: AsyncSession):
    """Удаляет все записи из таблицы users."""
    try:
        await session.execute(delete(User))
        await session.commit()
        print("✅ Все пользователи успешно удалены.")
    except SQLAlchemyError as e:
        await session.rollback()
        print(f"❌ Ошибка при удалении пользователей: {e}")


async def main():
    async for session in db_helper.session_getter():
        await delete_all_users(session)
        break


if __name__ == "__main__":
    asyncio.run(main())
