"""swap_lat_lng_and_add_registry_data

Revision ID: 5f49528fa1de
Revises: 833e09f0bf1a
Create Date: 2025-02-22 21:11:13.300546

"""
from typing import Sequence, Union
from datetime import datetime
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '5f49528fa1de'
down_revision: Union[str, None] = '833e09f0bf1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TARGET_TIMESTAMP = datetime(2025, 2, 22, 17, 43, 13, 578934)

def upgrade() -> None:
    # Add registry_data column
    op.add_column('nodes', sa.Column('registry_data', JSONB), schema='false_positive')

    connection = op.get_bind()
    
    # Get all nodes and their corresponding dam data after the target timestamp
    nodes = connection.execute(
        sa.text("""
            SELECT n.id, n.latitude, n.longitude, d.description
            FROM false_positive.nodes n
            LEFT JOIN false_positive.dams d ON d.id = n.id
            WHERE n.created_at >= :timestamp
        """),
        {"timestamp": TARGET_TIMESTAMP}
    ).fetchall()

    # For each affected node, swap coordinates and move description to registry_data if it exists
    for node in nodes:
        try:
            registry_data = json.loads(node.description) if node.description else None
        except (json.JSONDecodeError, AttributeError):
            registry_data = None

        # Update node
        connection.execute(
            sa.text("""
                UPDATE false_positive.nodes
                SET latitude = CAST(:longitude AS numeric),
                    longitude = CAST(:latitude AS numeric),
                    registry_data = CAST(:registry_data AS jsonb)
                WHERE id = CAST(:id AS uuid)
            """),
            {
                "id": str(node.id),
                "latitude": str(node.longitude),
                "longitude": str(node.latitude),
                "registry_data": json.dumps(registry_data) if registry_data is not None else None
            }
        )

        # If this node is a dam, clear its description
        if node.description is not None:
            connection.execute(
                sa.text("""
                    UPDATE false_positive.dams
                    SET description = ''
                    WHERE id = CAST(:id AS uuid)
                """),
                {"id": str(node.id)}
            )


def downgrade() -> None:
    connection = op.get_bind()
    
    # Get all affected nodes
    nodes = connection.execute(
        sa.text("""
            SELECT n.id, n.latitude, n.longitude, n.registry_data
            FROM false_positive.nodes n
            WHERE n.created_at >= :timestamp
        """),
        {"timestamp": TARGET_TIMESTAMP}
    ).fetchall()

    # Swap coordinates back and move registry_data back to description for dams
    for node in nodes:
        # Update node coordinates
        connection.execute(
            sa.text("""
                UPDATE false_positive.nodes
                SET latitude = CAST(:longitude AS numeric),
                    longitude = CAST(:latitude AS numeric)
                WHERE id = CAST(:id AS uuid)
            """),
            {
                "id": str(node.id),
                "latitude": str(node.longitude),
                "longitude": str(node.latitude)
            }
        )

        # If this node has registry_data and is a dam, move it back to description
        if node.registry_data is not None:
            connection.execute(
                sa.text("""
                    UPDATE false_positive.dams
                    SET description = :description
                    WHERE id = CAST(:id AS uuid)
                """),
                {
                    "id": str(node.id),
                    "description": json.dumps(node.registry_data)
                }
            )

    # Drop registry_data column
    op.drop_column('nodes', 'registry_data', schema='false_positive')
