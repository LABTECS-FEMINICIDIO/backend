import sys
from pathlib import Path
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Pegar a URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")

# Adicione o caminho para o diretório principal do projeto
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Importa o `Base` do seu módulo principal de modelos
from src.database.database import Base  # Substitua "your_project_name" pelo nome real do seu módulo

# Define o metadata para o Alembic
target_metadata = Base.metadata

# Configurações padrão do Alembic
config = context.config

# Substituir a URL do banco de dados no Alembic com o valor de DATABASE_URL
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
else:
    raise ValueError("A variável de ambiente DATABASE_URL não foi encontrada.")

def run_migrations_offline():
    """Executa migrações em modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Executa migrações em modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# Executa a migração dependendo do modo
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
