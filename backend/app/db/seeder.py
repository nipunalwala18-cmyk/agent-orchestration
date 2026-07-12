import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.role import Role
from app.models.permission import Permission

logger = logging.getLogger("platform.seeder")


async def seed_database(db: AsyncSession) -> None:
    """Seed permissions and default roles into the database."""
    # 1. Define permissions
    permissions_data = {
        "users:read": "Read users profile and listing",
        "users:write": "Create, modify, and delete users",
        "chat:read": "View chat history and conversations",
        "chat:write": "Send messages and chat with agents",
        "roles:read": "View role and permission mapping",
        "roles:write": "Modify role configurations",
    }

    # 2. Define roles and their permitted permission keys
    roles_data = {
        "Admin": {
            "description": "Administrator with full access to the system",
            "permissions": [
                "users:read",
                "users:write",
                "chat:read",
                "chat:write",
                "roles:read",
                "roles:write",
            ],
        },
        "Developer": {
            "description": "Developer with access to chat interfaces and user listings",
            "permissions": ["users:read", "chat:read", "chat:write"],
        },
        "User": {
            "description": "Standard client user with access to their own chat session",
            "permissions": ["chat:read", "chat:write"],
        },
    }

    # Check and insert permissions
    db_permissions = {}
    for name, desc in permissions_data.items():
        stmt = select(Permission).where(Permission.name == name)
        res = await db.execute(stmt)
        perm = res.scalars().first()
        if not perm:
            perm = Permission(name=name, description=desc)
            db.add(perm)
            logger.info(f"Seeding Permission: {name}")
        db_permissions[name] = perm

    await db.commit()

    # Refresh permissions to get primary keys
    for name in db_permissions:
        await db.refresh(db_permissions[name])

    # Check and insert roles
    for name, data in roles_data.items():
        stmt = select(Role).where(Role.name == name)
        res = await db.execute(stmt)
        role = res.scalars().first()
        if not role:
            role = Role(name=name, description=data["description"])
            db.add(role)
            logger.info(f"Seeding Role: {name}")
        else:
            # Refresh to fetch relationship collections safely
            await db.refresh(role)

        # Link permissions
        role.permissions = [db_permissions[p_name] for p_name in data["permissions"]]

    await db.commit()
    logger.info("Database seeding completed.")
