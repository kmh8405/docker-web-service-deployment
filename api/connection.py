import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DATABASE_URL에 있어야 하는 정보는 어떤 DB인지(mysql), 어떤 연결 라이브러리인지(pymysql), 계정정보(root), 구체적인 주소(여기서는 ip주소 없이 db라고만 써도 찾아갈 수 있음. 포트/db명)
DB_USER = "root"
DB_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST", "db")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_NAME = os.getenv("MYSQL_DATABASE")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

SessionFactory = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)