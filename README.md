# Book Marketplace FastAPI App

Учебное FastAPI-приложение на базе ветки `fourth_lection`.

Приложение доработано из простого каталога книг в платформу объявлений о продаже книг: появились продавцы, связь продавцов с книгами и JWT-авторизация для защищенных ручек.

## Что сделано

- Добавлена ORM-модель `Seller`.
- В модель `Book` добавлено поле `seller_id`.
- Настроена связь SQLAlchemy `Seller -> Book` один-ко-многим.
- При удалении продавца удаляются все его книги.
- Добавлены Pydantic-схемы для продавцов и токена.
- Добавлены сервисы и роутеры для продавцов и авторизации.
- Реализован JWT-токен по `e_mail + password`.
- Закрыты токеном:
  - `GET /api/v1/seller/{seller_id}`
  - `POST /api/v1/books/`
  - `PUT /api/v1/books/{book_id}`
- Добавлены тесты для книг, продавцов и авторизации.
- Обновлен `api_tests.http` с примерами запросов.

## Эндпоинты

### Продавцы

- `POST /api/v1/seller` — регистрация продавца.
- `GET /api/v1/seller` — список продавцов без поля `password`.
- `GET /api/v1/seller/{seller_id}` — продавец и его книги, нужен JWT.
- `PUT /api/v1/seller/{seller_id}` — обновление данных продавца без пароля и книг.
- `DELETE /api/v1/seller/{seller_id}` — удаление продавца вместе с его книгами.

### Авторизация

- `POST /api/v1/token` — получение JWT-токена.

Тело запроса:

```json
{
  "e_mail": "seller@example.com",
  "password": "secret"
}
```

Ответ:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

Защищенные ручки принимают токен стандартно:

```http
Authorization: Bearer <jwt-token>
```

### Книги

- `GET /api/v1/books/` — список книг.
- `POST /api/v1/books/` — создание книги, нужен JWT.
- `GET /api/v1/books/{book_id}` — получение книги.
- `PUT /api/v1/books/{book_id}` — обновление книги, нужен JWT.
- `PATCH /api/v1/books/{book_id}` — частичное обновление книги.
- `DELETE /api/v1/books/{book_id}` — удаление книги.

При создании и обновлении книги обязательно передается `seller_id`.

Пример создания книги:

```json
{
  "title": "Clean Architecture",
  "author": "Robert Martin",
  "count_pages": 300,
  "year": 2025,
  "seller_id": 1
}
```

## Быстрый запуск на Windows

Команды ниже нужно выполнять из корня проекта:

```powershell
cd path\to\shad_fastapi_project_2026
```

### 1. Поднять PostgreSQL

```powershell
docker compose up -d
```

Если Docker недоступен, можно использовать локальный PostgreSQL. Тогда нужно поменять параметры подключения в `.env` и заранее создать базы:

- `fastapi_project_db`
- `fastapi_project_test_db`

### 2. Создать виртуальное окружение

```powershell
python -m venv .venv
```

Если команда `python` недоступна, используйте Python Launcher:

```powershell
py -m venv .venv
```

### 3. Установить зависимости

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Создать `.env`

```powershell
Copy-Item .env_example .env
```

Пример `.env`:

```env
DB_USERNAME=postgres_user
DB_PASSWORD=postgres_pass
DB_HOST=127.0.0.1
DB_PORT=5445
DB_NAME=fastapi_project_db
JWT_SECRET_KEY=change-me-in-production
JWT_EXPIRE_SECONDS=3600
```

### 5. Запустить приложение

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

Swagger будет доступен по адресу:

```text
http://127.0.0.1:8000/docs
```

## Запуск тестов

PostgreSQL должен быть запущен.

Из корня проекта:

```powershell
.\.venv\Scripts\python.exe -m pytest src
```

Проверенный результат:

```text
18 passed
```

## Важное про базу данных

Приложение использует `BaseModel.metadata.create_all`, а не миграции Alembic. Это значит, что если таблицы уже были созданы до добавления `seller_id`, SQLAlchemy сам не изменит старую структуру таблицы.

Если приложение падает из-за старой схемы БД, проще всего пересоздать Docker-том/данные PostgreSQL и поднять базу заново.

## Структура проекта

- `src/configurations` — настройки приложения и подключение к БД.
- `src/models` — SQLAlchemy ORM-модели.
- `src/schemas` — Pydantic-схемы запросов и ответов.
- `src/services` — бизнес-логика и работа с БД.
- `src/routers` — FastAPI-роутеры.
- `src/tests` — pytest-тесты.

## Полезные ссылки

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM relationships](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)
- [FastAPI security tutorial](https://fastapi.tiangolo.com/tutorial/security/)
