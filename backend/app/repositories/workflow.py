from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import Workflow
from app.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    """Repository handling database operations for the Workflow model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Workflow, db)
