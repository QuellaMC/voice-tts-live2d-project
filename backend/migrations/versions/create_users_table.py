"""Create users table

Revision ID: create_users_table
Create Date: 2024-03-15 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from logging import getLogger

# revision identifiers, used by Alembic.
revision = 'create_users_table'
down_revision = None
branch_labels = None
depends_on = None

logger = getLogger(__name__)

def verify_table_does_not_exist(table_name: str) -> bool:
    """Verify that the table does not exist before creating it."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    return table_name not in inspector.get_table_names()

def upgrade() -> None:
    """Create users table with proper validation."""
    try:
        # Verify table doesn't exist
        if not verify_table_does_not_exist('users'):
            logger.warning("Users table already exists, skipping creation")
            return

        # Create users table with proper constraints
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(100), nullable=False),
            sa.Column('email', sa.String(255), nullable=False),
            sa.Column('hashed_password', sa.String(255), nullable=False),
            sa.Column(
                'role',
                sa.String(50),
                nullable=False,
                server_default='user',
                comment='User role: admin or user'
            ),
            sa.Column(
                'is_active',
                sa.Boolean(),
                nullable=False,
                server_default='true',
                comment='Whether the user account is active'
            ),
            sa.Column(
                'created_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('now()'),
                comment='Timestamp when the user was created'
            ),
            sa.Column(
                'last_login',
                sa.DateTime(),
                nullable=True,
                comment='Timestamp of last login'
            ),
            sa.PrimaryKeyConstraint('id'),
            sa.CheckConstraint(
                "role IN ('admin', 'user')",
                name='valid_role_check'
            ),
            sa.CheckConstraint(
                "length(username) >= 3",
                name='username_length_check'
            ),
            sa.CheckConstraint(
                "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
                name='email_format_check'
            )
        )

        # Create indexes with validation
        for index_name, column in [
            ('ix_users_username', 'username'),
            ('ix_users_email', 'email')
        ]:
            if index_name not in Inspector.from_engine(op.get_bind()).get_indexes('users'):
                op.create_index(index_name, 'users', [column], unique=True)

        logger.info("Successfully created users table and indexes")

    except Exception as e:
        logger.error(f"Failed to create users table: {str(e)}")
        raise

def downgrade() -> None:
    """Remove users table and related objects."""
    try:
        # Drop indexes first
        for index_name in ['ix_users_email', 'ix_users_username']:
            op.drop_index(index_name)
            logger.info(f"Dropped index {index_name}")

        # Drop the table
        op.drop_table('users')
        logger.info("Successfully dropped users table")

    except Exception as e:
        logger.error(f"Failed to drop users table: {str(e)}")
        raise 