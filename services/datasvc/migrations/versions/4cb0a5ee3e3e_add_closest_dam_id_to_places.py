"""add_closest_dam_id_to_places

Revision ID: 4cb0a5ee3e3e
Revises: cdb748836b5c
Create Date: 2025-02-23 01:08:21.138338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4cb0a5ee3e3e'
down_revision: Union[str, None] = 'cdb748836b5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add closest_dam_id column to places table
    op.add_column('places', sa.Column('closest_dam_id', postgresql.UUID(as_uuid=True), nullable=True), schema='false_positive')
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_places_closest_dam_id_dams',
        'places',
        'dams',
        ['closest_dam_id'],
        ['id'],
        source_schema='false_positive',
        referent_schema='false_positive'
    )


def downgrade() -> None:
    # Drop foreign key constraint first
    op.drop_constraint('fk_places_closest_dam_id_dams', 'places', schema='false_positive', type_='foreignkey')
    
    # Drop the column
    op.drop_column('places', 'closest_dam_id', schema='false_positive')
