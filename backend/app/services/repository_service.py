from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.github_installation import GitHubInstallation
from app.models.repository import Repository


async def get_repository_for_installation(
    db: AsyncSession,
    installation_id: int,
    github_repository_id: int,
) -> Repository | None:
    """
    Find a repository belonging to a specific
    GitHub App installation.
    """

    result = await db.execute(
        select(Repository)
        .join(
            GitHubInstallation,
            Repository.github_installation_id
            == GitHubInstallation.id,
        )
        .where(
            GitHubInstallation.installation_id
            == installation_id,
            Repository.github_repository_id
            == github_repository_id,
        )
    )

    return result.scalar_one_or_none()