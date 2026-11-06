
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache

COPY . .

RUN uv run python src/manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "uv run python src/manage.py migrate && uv run gunicorn --chdir src --bind 0.0.0.0:${PORT:-8000} settings.wsgi:application"]
