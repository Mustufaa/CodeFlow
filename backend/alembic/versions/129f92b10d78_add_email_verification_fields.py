"""add email verification fields

Revision ID: 129f92b10d78
Revises: d062ec04c8cf
Create Date: 2026-08-02 14:28:45.336596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '129f92b10d78'
down_revision: Union[str, Sequence[str], None] = 'd062ec04c8cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column(
            'is_verified',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        'users',
        sa.Column('verification_token', sa.String(length=255), nullable=True),
    )
    op.create_unique_constraint(
        'uq_users_verification_token',
        'users',
        ['verification_token'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'uq_users_verification_token',
        'users',
        type_='unique',
    )
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'is_verified')
