# auth_user
## Мини-проект с авторизацией на FastAPI, PostgreSQL, JWT и Redis.

### Технологии
- FastAPI
- SQLAlchemy + AsyncPG
- JWT
- Redis
- Pydantic
- Passlib

### Установка
1. клонируйте репозиторий
```bash
git clone https://github.com/stillyc1/auth_user.git
cd auth_user
```
```bash
poetry install
cd auth-user
```
3. Создайте базу данных в postgresql - auth_user
4. Примените миграции
```bash
alembic upgrade head
```
4. запустите redis
5. локальный запуск для проверки
```bash
uvicorn main:main_app --host 127.0.0.1
```
