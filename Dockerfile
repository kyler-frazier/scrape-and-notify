FROM python:3.10-slim

# Set environment variables
ENV CONTAINER=docker \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry: Don't create virtual environment, we're in a container
ENV POETRY_VENV_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies only (without the current project for better caching)
RUN poetry install --no-root

# Copy application code
COPY src/scrape_and_notify ./src/scrape_and_notify

# Install only the current project (dependencies already installed)
RUN poetry install --only-root

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Command to run the application
CMD ["poetry", "run", "scrape-and-notify"]
