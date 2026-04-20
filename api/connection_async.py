import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DB_USER = "root"
DB_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST", "db")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_NAME = os.getenv("MYSQL_DATABASE")

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)

AsyncSessionFactory = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)
