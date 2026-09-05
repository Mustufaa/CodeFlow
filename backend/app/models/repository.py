from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Repository(Base):
    __tablename__ = "repositories"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "github_repository_id",
            name="uq_tenant_github_repository",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    github_installation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "github_installations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    github_repository_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    private: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    default_branch: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )