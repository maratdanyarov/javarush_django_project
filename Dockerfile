FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV and add to PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (creates .venv by default)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Collect static files using uv run
RUN uv run python manage.py collectstatic --noinput

EXPOSE 8000

# Run server using uv run
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]