"""add_postgis_and_pgrouting_extensions

Revision ID: cdb748836b5c
Revises: add_edges_table
Create Date: 2025-02-22 22:59:11.685190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdb748836b5c'
down_revision: Union[str, None] = 'add_edges_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    # Create pgRouting extension
    op.execute('CREATE EXTENSION IF NOT EXISTS pgrouting')


def downgrade() -> None:
    # Drop pgRouting extension first as it depends on PostGIS
    op.execute('DROP EXTENSION IF EXISTS pgrouting')
    # Drop PostGIS extension
    op.execute('DROP EXTENSION IF EXISTS postgis')
