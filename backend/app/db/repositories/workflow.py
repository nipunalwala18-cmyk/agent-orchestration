from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.base import BaseRepository
from app.db.models import Workflow


class WorkflowRepository(BaseRepository[Workflow]):
    """Repository handling database operations for the Workflow model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Workflow, db)
