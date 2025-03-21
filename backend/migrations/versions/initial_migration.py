"""Initial database migration

Revision ID: initial
Create Date: 2024-02-26 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "initial"
down_revision = None  # This should be None as it's the initial migration
branch_labels = None
depends_on = (
    "create_users_table"  # Depends on users table but not in the migration chain
)


def upgrade() -> None:
    # Create concepts table
    op.create_table(
        "concepts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.ForeignKeyConstraint(["parent_id"], ["concepts.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_concepts_name", "concepts", ["name"])

    # Create tags table
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_tags_name", "tags", ["name"])

    # Create knowledge table with vector embeddings support
    op.create_table(
        "knowledge",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("topic"),
    )
    op.create_index("ix_knowledge_topic", "knowledge", ["topic"])

    # Create knowledge_tags association table
    op.create_table(
        "knowledge_tags",
        sa.Column("knowledge_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_id"], ["knowledge.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("knowledge_id", "tag_id"),
    )

    # Create knowledge_concepts association table
    op.create_table(
        "knowledge_concepts",
        sa.Column("knowledge_id", sa.Integer(), nullable=False),
        sa.Column("concept_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_id"], ["knowledge.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("knowledge_id", "concept_id"),
    )


def downgrade() -> None:
    op.drop_table("knowledge_concepts")
    op.drop_table("knowledge_tags")
    op.drop_index("ix_knowledge_topic", "knowledge")
    op.drop_table("knowledge")
    op.drop_index("ix_tags_name", "tags")
    op.drop_table("tags")
    op.drop_index("ix_concepts_name", "concepts")
    op.drop_table("concepts")
