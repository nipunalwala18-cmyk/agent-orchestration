from unittest.mock import AsyncMock, MagicMock
import uuid
from httpx import AsyncClient
import pytest

from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_register_success(client: AsyncClient, mock_db: AsyncMock) -> None:
    """Test user registration endpoint."""
    user_role = Role(name="User", description="Default role")

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.side_effect = [None, user_role]
    mock_db.execute.return_value = mock_result

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@test.com", "password": "securepassword123"},
    )

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["email"] == "newuser@test.com"


async def test_login_success(client: AsyncClient, mock_db: AsyncMock) -> None:
    """Test successful user login endpoint."""
    hashed_password = get_password_hash("securepassword123")
    user = User(
        id=uuid.uuid4(),
        email="testuser@test.com",
        hashed_password=hashed_password,
        is_active=True,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = user
    mock_db.execute.return_value = mock_result

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@test.com", "password": "securepassword123"},
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "access_token" in json_data["data"]
    assert "refresh_token" in json_data["data"]


async def test_get_me_success(client: AsyncClient, mock_db: AsyncMock) -> None:
    """Test authenticated profile fetch endpoint."""
    user = User(
        id=uuid.uuid4(),
        email="activeuser@test.com",
        hashed_password="somehashpassword",
        is_active=True,
        roles=[],
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = user
    mock_db.execute.return_value = mock_result

    from app.core.security import create_access_token

    token = create_access_token(subject=user.id)

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["email"] == "activeuser@test.com"


async def test_google_login_new_user_success(
    client: AsyncClient, mock_db: AsyncMock
) -> None:
    """Test Google login flow when registering a new user."""
    user_role = Role(name="User", description="Default role")

    mock_result = MagicMock()
    # 1. get_by_email returns None (user doesn't exist)
    # 2. get_by_name returns user_role
    mock_result.scalars.return_value.first.side_effect = [None, user_role]
    mock_db.execute.return_value = mock_result

    response = await client.post(
        "/api/v1/auth/google",
        json={"id_token": "mock_newgoogleuser@test.com"},
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "access_token" in json_data["data"]
    assert "refresh_token" in json_data["data"]


async def test_google_login_existing_user_success(
    client: AsyncClient, mock_db: AsyncMock
) -> None:
    """Test Google login flow when user already exists in DB."""
    existing_user = User(
        id=uuid.uuid4(),
        email="existinggoogleuser@test.com",
        hashed_password=None,
        is_active=True,
    )

    mock_result = MagicMock()
    # get_by_email returns existing_user
    mock_result.scalars.return_value.first.return_value = existing_user
    mock_db.execute.return_value = mock_result

    response = await client.post(
        "/api/v1/auth/google",
        json={"id_token": "mock_existinggoogleuser@test.com"},
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "access_token" in json_data["data"]
    assert "refresh_token" in json_data["data"]

