FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user early
RUN adduser --disabled-password --gecos '' appuser

# Install Poetry
RUN pip install poetry

# Configure Poetry: Don't create virtual environment, we're in a container
ENV POETRY_VENV_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

# Set work directory and change ownership
WORKDIR /app
RUN chown appuser:appuser /app

# Switch to appuser for all Poetry operations
USER appuser

# Copy Poetry files
COPY --chown=appuser:appuser pyproject.toml poetry.lock* ./

# Install dependencies only (without the current project for better caching)
RUN poetry install --no-root

# Copy application code
COPY --chown=appuser:appuser src/scrape_and_notify ./src/scrape_and_notify

# Install only the current project (dependencies already installed)
RUN poetry install --only-root

# Command to run the application
CMD ["poetry", "run", "scrape-and-notify"]