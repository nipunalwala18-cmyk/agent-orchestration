from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.workflow import WorkflowRepository
from app.db.models import Workflow


class WorkflowService:
    """Service layer coordinating business logic around Workflows."""

    def __init__(self, db: AsyncSession) -> None:
        self.workflow_repo = WorkflowRepository(db)

    async def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        """Fetch a workflow definition by database identifier."""
        return await self.workflow_repo.get(workflow_id)

    async def list_workflows(self, skip: int = 0, limit: int = 100) -> List[Workflow]:
        """Fetch a paginated list of workflow definitions."""
        return await self.workflow_repo.get_all(skip, limit)

    async def create_workflow(self, workflow: Workflow) -> Workflow:
        """Create and store a new workflow definition database record."""
        return await self.workflow_repo.create(workflow)

    async def delete_workflow(self, workflow_id: int) -> bool:
        """Delete an existing workflow definition database record."""
        return await self.workflow_repo.delete(workflow_id)
