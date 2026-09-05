import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.tenant import Tenant
from app.models.tenant_member import TenantMember
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantResponse


router = APIRouter(
    prefix="/api/tenants",
    tags=["Tenants"],
)


def generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")

    if not slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant name.",
        )

    return slug


@router.post(
    "/",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Generate tenant slug
    slug = generate_slug(tenant_data.name)

    # Check whether tenant already exists
    existing_tenant = await db.scalar(
        select(Tenant).where(Tenant.slug == slug)
    )

    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tenant with this name already exists.",
        )

    # Create tenant
    tenant = Tenant(
        name=tenant_data.name,
        slug=slug,
    )

    db.add(tenant)

    # Get generated tenant ID before commit
    await db.flush()

    # Make current user the tenant owner
    tenant_member = TenantMember(
        tenant_id=tenant.id,
        user_id=current_user.id,
        role="OWNER",
    )

    db.add(tenant_member)

    # Save tenant + membership together
    await db.commit()

    await db.refresh(tenant)

    return tenant