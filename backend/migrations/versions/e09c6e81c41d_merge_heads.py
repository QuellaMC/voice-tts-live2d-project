"""merge_heads

Revision ID: e09c6e81c41d
Revises: add_groups_and_permissions, initial
Create Date: 2025-03-21 02:54:08.563237

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e09c6e81c41d"
down_revision = ("add_groups_and_permissions", "initial")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
