FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry or use pip. Using pip as initialized in this session.
COPY pyproject.toml .
# We didn't use poetry.lock, so valid. 
# But we installed dependencies via pip on host. 
# We should generate requirements.txt or install via pip.
# Let's use pip install directly for packages mentioned in pyproject.
# Or better, install poetry and use it.
# Let's stick to pip to be simple and robust.

RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    "sqlalchemy[asyncio]" \
    asyncpg \
    redis \
    alembic \
    pydantic-settings \
    "python-jose[cryptography]" \
    "passlib[argon2]" \
    python-multipart \
    email-validator \
    transformers \
    torch

COPY . .

# Expose port
EXPOSE 8000

# Command to run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
