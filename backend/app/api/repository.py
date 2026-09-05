from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.tenant_member import TenantMember
from app.models.github_installation import GitHubInstallation
from app.models.repository import Repository
from app.schemas.repository import RepositoryConnect, RepositoryResponse
from app.github.client import GitHubClient


router = APIRouter(
    prefix="/api/tenants/{tenant_id}/repositories",
    tags=["Repositories"],
)


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def connect_repository(
    tenant_id: int,
    data: RepositoryConnect,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # --------------------------------------------------
    # 1. Check tenant exists
    # --------------------------------------------------
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # --------------------------------------------------
    # 2. Check current user is OWNER of the tenant
    # --------------------------------------------------
    member_result = await db.execute(
        select(TenantMember).where(
            TenantMember.tenant_id == tenant_id,
            TenantMember.user_id == current_user.id,
        )
    )
    member = member_result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this tenant",
        )

    if member.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant owners can connect repositories",
        )

    # --------------------------------------------------
    # 3. Get GitHub installation connected to tenant
    # --------------------------------------------------
    installation_result = await db.execute(
        select(GitHubInstallation).where(
            GitHubInstallation.tenant_id == tenant_id
        )
    )
    installation = installation_result.scalar_one_or_none()

    if not installation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GitHub installation connected to this tenant",
        )

    # --------------------------------------------------
    # 4. Fetch repository from GitHub
    # --------------------------------------------------
    github_client = GitHubClient()

    try:
        github_repo = await github_client.get_repository(
            installation_id=installation.installation_id,
            owner=data.owner,
            repo=data.name,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # --------------------------------------------------
    # 5. Prevent duplicate repository
    # --------------------------------------------------
    existing_result = await db.execute(
        select(Repository).where(
            Repository.tenant_id == tenant_id,
            Repository.github_repository_id == github_repo["id"],
        )
    )
    existing_repo = existing_result.scalar_one_or_none()

    if existing_repo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Repository is already connected to this tenant",
        )

    # --------------------------------------------------
    # 6. Save repository
    # --------------------------------------------------
    repository = Repository(
        tenant_id=tenant_id,
        github_installation_id=installation.id,
        github_repository_id=github_repo["id"],
        owner=github_repo["owner"]["login"],
        name=github_repo["name"],
        full_name=github_repo["full_name"],
        private=github_repo["private"],
        default_branch=github_repo["default_branch"],
    )

    db.add(repository)
    await db.commit()
    await db.refresh(repository)

    return repository

@router.get(
    "",
    response_model=list[RepositoryResponse],
)
async def list_repositories(
    tenant_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # --------------------------------------------------
    # 1. Check tenant exists
    # --------------------------------------------------
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # --------------------------------------------------
    # 2. Check current user is a tenant member
    # --------------------------------------------------
    member_result = await db.execute(
        select(TenantMember).where(
            TenantMember.tenant_id == tenant_id,
            TenantMember.user_id == current_user.id,
        )
    )
    member = member_result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this tenant",
        )

    # --------------------------------------------------
    # 3. Fetch connected repositories
    # --------------------------------------------------
    repositories_result = await db.execute(
        select(Repository)
        .where(Repository.tenant_id == tenant_id)
        .order_by(Repository.id.desc())
    )

    repositories = repositories_result.scalars().all()

    return repositories