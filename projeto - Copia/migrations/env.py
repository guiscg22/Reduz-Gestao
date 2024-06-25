from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os
import sys

# adicionando o caminho do aplicativo ao sys.path para que possamos importar
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from models import db

# obtendo a configuração do aplicativo Flask
config = context.config

# interpretando o arquivo de configuração para Python logging
fileConfig(config.config_file_name)
logger = context.getLogger('alembic.env')

# adicionando o MetaData do modelo ao contexto para suporte ao 'autogenerate'
target_metadata = db.metadata

# configuração de conexão do banco de dados
config.set_main_option('sqlalchemy.url', os.environ.get('DATABASE_URL'))

def run_migrations_offline():
    """Executar migrações no modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Executar migrações no modo 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
