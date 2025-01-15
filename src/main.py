from typing import AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import db
from .config import settings
from . import models, schemas


app = FastAPI(title="Book Inventory API")


@app.on_event("startup")
async def startup():
    db.init(settings.DATABASE_URL)


@app.on_event("shutdown")
async def shutdown():
    await db.close()


# Dependency for routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db.get_session():
        yield session


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/books/", response_model=schemas.Book)
async def create_book(
    book: schemas.BookCreate, db_session: AsyncSession = Depends(get_db)
):
    db_book = models.Book(**book.model_dump())
    db_session.add(db_book)
    await db_session.commit()
    await db_session.refresh(db_book)
    return db_book


@app.get("/books/", response_model=list[schemas.Book])
async def list_books(
    skip: int = 0, limit: int = 100, db_session: AsyncSession = Depends(get_db)
):
    query = select(models.Book).offset(skip).limit(limit)
    result = await db_session.execute(query)
    books = result.scalars().all()
    return books


@app.get("/books/{book_id}", response_model=schemas.Book)
async def get_book(book_id: int, db_session: AsyncSession = Depends(get_db)):
    query = select(models.Book).filter(models.Book.id == book_id)
    result = await db_session.execute(query)
    book = result.scalar_one_or_none()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
