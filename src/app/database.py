import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nlq_demo.db")
engine = create_engine(DATABASE_URL)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                month TEXT NOT NULL,
                total REAL NOT NULL,
                approved_orders INTEGER NOT NULL
            )
        """))
        count = conn.execute(text("SELECT COUNT(*) FROM sales")).scalar_one()
        if count == 0:
            conn.execute(text("""
                INSERT INTO sales (month,total,approved_orders) VALUES
                ('agosto',1250000,42),
                ('setembro',980000,35)
            """))

def execute_readonly(sql: str):
    normalized = sql.strip().lower()
    if not normalized.startswith("select"):
        raise ValueError("Only SELECT statements are permitted.")
    forbidden = ("insert ", "update ", "delete ", "drop ", "alter ", "create ", "pragma ", "attach ")
    if any(x in normalized for x in forbidden):
        raise ValueError("Unsafe SQL rejected.")
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).mappings().all()
        return [dict(r) for r in rows]
