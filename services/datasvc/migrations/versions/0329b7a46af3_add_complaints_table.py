"""add complaints table

Revision ID: 0329b7a46af3
Revises: 4cb0a5ee3e3e
Create Date: 2025-02-23 03:40:43.455772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0329b7a46af3'
down_revision: Union[str, None] = '4cb0a5ee3e3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create complaints table using existing enum
    op.create_table('complaints',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_email', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'resolved', name='complaint_status', schema='false_positive', create_type=False), nullable=False, server_default='pending'),
        sa.Column('place_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('dam_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dam_id'], ['false_positive.dams.id'], ),
        sa.ForeignKeyConstraint(['place_id'], ['false_positive.places.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='false_positive'
    )


def downgrade() -> None:
    # Drop complaints table
    op.drop_table('complaints', schema='false_positive')
