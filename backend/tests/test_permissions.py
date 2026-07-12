from unittest.mock import AsyncMock, MagicMock
import uuid
from httpx import AsyncClient
import pytest

from app.core.security import create_access_token
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_list_users_denied_without_permission(
    client: AsyncClient, mock_db: AsyncMock
) -> None:
    """Verify that a user without the 'users:read' permission receives a 403 Forbidden."""
    user = User(
        id=uuid.uuid4(),
        email="unprivileged@test.com",
        hashed_password="somehashpassword",
        is_active=True,
        roles=[],
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = user
    mock_db.execute.return_value = mock_result

    token = create_access_token(subject=user.id)

    response = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    json_data = response.json()
    assert json_data["success"] is False
    assert "Permission denied" in json_data["message"]


async def test_list_users_allowed_with_permission(
    client: AsyncClient, mock_db: AsyncMock
) -> None:
    """Verify that a user with the 'users:read' permission can view the user list."""
    perm = Permission(name="users:read", description="Read users")
    role = Role(name="Admin", description="Admin role", permissions=[perm])
    user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        hashed_password="somehashpassword",
        is_active=True,
        roles=[role],
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = user
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    token = create_access_token(subject=user.id)

    response = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"] == []
