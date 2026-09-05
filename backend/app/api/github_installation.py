from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db

from app.models.user import User
from app.models.tenant import Tenant
from app.models.tenant_member import TenantMember
from app.models.github_installation import GitHubInstallation

from app.schemas.github_installation import (
    GitHubInstallationConnect,
    GitHubInstallationResponse,
)

from app.github.auth import get_github_app_installations


router = APIRouter(
    prefix="/api/tenants",
    tags=["GitHub Installations"],
)


@router.post(
    "/{tenant_id}/github/installations",
    response_model=GitHubInstallationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def connect_github_installation(
    tenant_id: int,
    installation_data: GitHubInstallationConnect,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check tenant exists
    tenant = await db.scalar(
        select(Tenant).where(Tenant.id == tenant_id)
    )

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        )

    # Check current user belongs to tenant
    membership = await db.scalar(
        select(TenantMember).where(
            TenantMember.tenant_id == tenant_id,
            TenantMember.user_id == current_user.id,
        )
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this tenant.",
        )

    # Only OWNER can connect GitHub installation
    if membership.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the tenant owner can connect GitHub.",
        )

    # Fetch actual GitHub App installations
    installations = await get_github_app_installations()

    github_installation = None

    for installation in installations:
        if installation.get("id") == installation_data.installation_id:
            github_installation = installation
            break

    if not github_installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub App installation not found.",
        )

    # Extract GitHub account information
    account = github_installation.get("account") or {}

    account_login = account.get("login")
    account_type = account.get("type")

    if not account_login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub account information is missing.",
        )

    # Check whether installation is already connected
    existing_installation = await db.scalar(
        select(GitHubInstallation).where(
            GitHubInstallation.installation_id
            == installation_data.installation_id
        )
    )

    if existing_installation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="GitHub installation is already connected.",
        )

    # Save installation
    installation = GitHubInstallation(
        tenant_id=tenant_id,
        installation_id=installation_data.installation_id,
        account_login=account_login,
        account_type=account_type or "Unknown",
    )

    db.add(installation)

    await db.commit()
    await db.refresh(installation)

    return installation