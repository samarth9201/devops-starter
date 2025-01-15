from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
import pytest
from src.main import create_book, list_books, get_book
from src.models import Book
from src.schemas import BookCreate
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_create_book_unit(mock_db):
    # Arrange
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        price=29.99)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    # Act
    result = await create_book(book_data, mock_db)

    # Assert
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called
    assert result.title == "Test Book"
    assert result.author == "Test Author"
    assert result.price == 29.99


@pytest.mark.asyncio
async def test_list_books_unit(mock_db):
    # Arrange
    mock_books = [
        Book(
            id=1,
            title="Book 1",
            author="Author 1",
            price=19.99,
            created_at=datetime.now(),
        ),
        Book(
            id=2,
            title="Book 2",
            author="Author 2",
            price=29.99,
            created_at=datetime.now(),
        ),
    ]
    mock_result = Mock()
    mock_result.scalars().all.return_value = mock_books
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await list_books(db_session=mock_db)

    # Assert
    assert mock_db.execute.called
    assert len(result) == 2
    assert result[0].title == "Book 1"
    assert result[1].title == "Book 2"


@pytest.mark.asyncio
async def test_get_book_unit(mock_db):
    # Arrange
    mock_book = Book(
        id=1,
        title="Test Book",
        author="Test Author",
        price=29.99,
        created_at=datetime.now(),
    )
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_book
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await get_book(1, mock_db)

    # Assert
    assert mock_db.execute.called
    assert result.id == 1
    assert result.title == "Test Book"


@pytest.mark.asyncio
async def test_get_nonexistent_book_unit(mock_db):
    # Arrange
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_book(999, mock_db)
    assert exc_info.value.status_code == 404
