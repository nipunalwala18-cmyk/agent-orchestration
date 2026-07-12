from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.role import Role
from app.models.permission import Permission
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository handling database operations for the Role model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Role, db)

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Fetch a single role by its name with permissions loaded."""
        result = await self.db.execute(
            select(Role)
            .filter(Role.name == name)
            .options(selectinload(Role.permissions))
        )
        return result.scalars().first()


class PermissionRepository(BaseRepository[Permission]):
    """Repository handling database operations for the Permission model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Permission, db)

    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Fetch a single permission by its name."""
        result = await self.db.execute(
            select(Permission)
            .filter(Permission.name == name)
        )
        return result.scalars().first()
