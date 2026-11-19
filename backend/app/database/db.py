import os, json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
URL=os.getenv("DATABASE_URL", "sqlite:///./blocklab.db")
kwargs={"check_same_thread":False} if URL.startswith("sqlite") else {}
engine=create_engine(URL, connect_args=kwargs, future=True)
Session=sessionmaker(bind=engine, expire_on_commit=False)
def init_db():
    with engine.begin() as c:
        c.execute(text("CREATE TABLE IF NOT EXISTS snapshots (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)"))
def save_snapshot(payload: dict):
    with engine.begin() as c:
        c.execute(text("DELETE FROM snapshots")); c.execute(text("INSERT INTO snapshots(payload) VALUES (:p)"), {"p":json.dumps(payload)})
def load_snapshot():
    with engine.connect() as c:
        row=c.execute(text("SELECT payload FROM snapshots ORDER BY id DESC LIMIT 1")).first()
        return json.loads(row[0]) if row else None
