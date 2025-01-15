import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_book(test_client: AsyncClient):
    response = await test_client.post(
        "/books/", json={"title": "Test Book", "author": "Test Author", "price": 29.99}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["price"] == 29.99
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_books(test_client: AsyncClient):
    # Create a test book first
    await test_client.post(
        "/books/",
        json={"title": "Another Test Book", "author": "Another Author", "price": 19.99},
    )

    response = await test_client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_book(test_client: AsyncClient):
    # Create a test book first
    create_response = await test_client.post(
        "/books/",
        json={"title": "Get Test Book", "author": "Get Test Author", "price": 39.99},
    )
    book_id = create_response.json()["id"]

    response = await test_client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get Test Book"
    assert data["author"] == "Get Test Author"
    assert data["price"] == 39.99


@pytest.mark.asyncio
async def test_get_nonexistent_book(test_client: AsyncClient):
    response = await test_client.get("/books/9999")
    assert response.status_code == 404
