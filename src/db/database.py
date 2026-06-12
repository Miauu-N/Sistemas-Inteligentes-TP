import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Leer la URL de la base de datos de las variables de entorno
# Se usará SQLite en memoria o en archivo temporalmente para desarrollo si no hay Postgres
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./cv_analyzer.db")

# Reemplazar postgres:// por postgresql:// (requerido por SQLAlchemy para compatibilidad de Heroku/Render)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    # Para SQLite en local, se necesita args para no checkear el mismo thread, pero asyncpg no lo usa
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    """Dependencia de FastAPI para obtener la sesión de DB."""
    async with AsyncSessionLocal() as session:
        yield session
