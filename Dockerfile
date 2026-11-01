FROM python:3.12-slim

# Variables para que Python corra fluido en contenedores
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar uv dentro del contenedor
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar los archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalar las dependencias del proyecto
RUN uv sync --frozen --no-cache

# Copiar todo el código fuente al contenedor
COPY . .

# Exponer el puerto por el que va a responder Django
EXPOSE 8000

# Comando para arrancar el servidor
CMD ["uv", "run", "src/manage.py", "runserver", "0.0.0.0:8000"]