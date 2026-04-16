from fastapi import FastAPI
from sqlalchemy import text
from connection import SessionFactory

app = FastAPI()

@app.get("/health-check")
def health_check_handler():
    with SessionFactory() as session:
        stmt = text("SELECT * FROM user LIMIT 1;")
        row = session.execute(stmt).fetchone() # Row 객체로 변환
    return {"user": row._asdict()} # Row -> dict로 변환하기 위해 ._asdict() 사용
