FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install alembic for database migrations
RUN pip install alembic

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/uploads /app/data/models /app/data/datasets

# Create alembic.ini if not exists
RUN if [ ! -f alembic.ini ]; then \
    echo "[alembic]\n\
sqlalchemy.url = postgresql://legal_user:legal_password@postgres:5432/legal_models\n\
script_location = alembic\n\
prepend_sys_path = .\n\
version_path_separator = os\n\
\n\
[loggers]\n\
keys = root,sqlalchemy,alembic\n\
\n\
[handlers]\n\
keys = console\n\
\n\
[formatters]\n\
keys = generic\n\
\n\
[logger_root]\n\
level = WARN\n\
handlers = console\n\
qualname =\n\
\n\
[logger_sqlalchemy]\n\
level = WARN\n\
handlers =\n\
qualname = sqlalchemy.engine\n\
\n\
[logger_alembic]\n\
level = INFO\n\
handlers =\n\
qualname = alembic\n\
\n\
[handler_console]\n\
class = StreamHandler\n\
args = (sys.stderr,)\n\
level = NOTSET\n\
formatter = generic\n\
\n\
[formatter_generic]\n\
format = %(levelname)-5.5s [%(name)s] %(message)s\n\
datefmt = %H:%M:%S" > alembic.ini; \
fi

# Create alembic directory and env.py
RUN mkdir -p alembic/versions && \
    echo "from logging.config import fileConfig\n\
from sqlalchemy import engine_from_config\n\
from sqlalchemy import pool\n\
from alembic import context\n\
import sys\n\
import os\n\
\n\
sys.path.append(os.getcwd())\n\
\n\
from app.database.session import Base\n\
from app.auth.models import *\n\
\n\
config = context.config\n\
\n\
if config.config_file_name is not None:\n\
    fileConfig(config.config_file_name)\n\
\n\
target_metadata = Base.metadata\n\
\n\
def run_migrations_offline() -> None:\n\
    url = config.get_main_option(\"sqlalchemy.url\")\n\
    context.configure(\n\
        url=url,\n\
        target_metadata=target_metadata,\n\
        literal_binds=True,\n\
        dialect_opts={\"paramstyle\": \"named\"},\n\
    )\n\
\n\
    with context.begin_transaction():\n\
        context.run_migrations()\n\
\n\
def run_migrations_online() -> None:\n\
    connectable = engine_from_config(\n\
        config.get_section(config.config_ini_section, {}),\n\
        prefix=\"sqlalchemy.\",\n\
        poolclass=pool.NullPool,\n\
    )\n\
\n\
    with connectable.connect() as connection:\n\
        context.configure(\n\
            connection=connection, target_metadata=target_metadata\n\
        )\n\
\n\
        with context.begin_transaction():\n\
            context.run_migrations()\n\
\n\
if context.is_offline_mode():\n\
    run_migrations_offline()\n\
else:\n\
    run_migrations_online()" > alembic/env.py

# Create initial migration
RUN alembic revision --autogenerate -m "Initial migration"

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]