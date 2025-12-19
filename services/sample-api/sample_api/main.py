from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import SessionLocal, init_db
from .models import Item


@asynccontextmanager
async def lifespan(app: FastAPI):
    # temporary schema bootstrap (since we are skipping Alembic)
    init_db()
    yield


app = FastAPI(title="sample-api", lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/items")
def create_item(payload: dict, db: Session = Depends(get_db)):
    name = (payload or {}).get("name")
    if not name or not isinstance(name, str):
        raise HTTPException(status_code=400, detail="name is required")

    item = Item(name=name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name}


@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    items = db.query(Item).order_by(Item.id.asc()).all()
    return [{"id": i.id, "name": i.name} for i in items]
