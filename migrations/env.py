"""Alembic environment.

The database URL comes from application settings, never from
alembic.ini, so there is exactly one place configuration lives and no
second copy to drift or to leak a credential into a tracked file.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from rolecall.config import get_settings
from rolecall.db import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Autogenerate compares the models' declared metadata to the live schema.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit migration SQL without a live database connection."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations against the configured database."""
    connectable = create_engine(get_settings().database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
