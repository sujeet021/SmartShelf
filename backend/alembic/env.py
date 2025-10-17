# Minimal alembic env for reference. In production configure alembic properly.
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from alembic import context
from app.db.base import Base
from app.core.config import settings
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix='sqlalchemy.',
    poolclass=None,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection,target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
if context.is_offline_mode():
    pass
else:
    run_migrations_online()