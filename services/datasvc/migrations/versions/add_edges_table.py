"""Add edges table

Revision ID: add_edges_table
Revises: 2325ffcb8908
Create Date: 2024-03-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_edges_table'
down_revision: str = '2325ffcb8908'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('edges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('distance', sa.Numeric(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['source_node_id'], ['false_positive.nodes.id'], ),
        sa.ForeignKeyConstraint(['target_node_id'], ['false_positive.nodes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='false_positive'
    )


def downgrade() -> None:
    op.drop_table('edges', schema='false_positive') 