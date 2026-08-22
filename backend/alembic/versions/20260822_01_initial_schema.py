"""Create the initial application schema.

Revision ID: 20260822_01
Revises:
Create Date: 2026-08-22
"""

from alembic import op

from app.core.database import Base
from app.models import domain  # noqa: F401 - registers all ORM models

revision = "20260822_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
