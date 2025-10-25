import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import router as api_router
from core.config import settings
from core.models import db_helper
from core.redis import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Проверяем соединение с redis
    await redis.ping()
    sys.stdout.write("\033[92mINFO:\033[0m     Redis подключён.\n")

    # startup
    yield

    if redis is not None:
        await redis.close()
        sys.stdout.write("\033[92mINFO:\033[0m     Redis отключён.\n")

    # shutdown
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(
    api_router,
    prefix=settings.api.prefix,
)


if __name__ == "__main__":
    uvicorn.run(
        app="main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )

# uvicorn main:main_app --host 127.0.0.1 --reload --- "Локальный старт"
# alembic revision --autogenerate -m "create Users model" --- "Создание миграций"
# alembic upgrade head --- "Применение миграций"
# alembic downgrade base \ -1 --- "откатить миграции до базовой \ до предыдущей"
