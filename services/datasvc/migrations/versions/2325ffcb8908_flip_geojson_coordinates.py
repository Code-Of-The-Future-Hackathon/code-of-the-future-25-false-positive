"""flip_geojson_coordinates

Revision ID: 2325ffcb8908
Revises: 5f49528fa1de
Create Date: 2025-02-22 21:54:16.736581

"""
from typing import Sequence, Union
from datetime import datetime
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2325ffcb8908'
down_revision: Union[str, None] = '5f49528fa1de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TARGET_TIMESTAMP = datetime(2025, 2, 22, 17, 43, 13, 578934)

def flip_coordinates(geojson):
    """Flip coordinates in a GeoJSON object."""
    if not geojson or not isinstance(geojson, dict):
        return geojson

    if geojson.get('type') == 'MultiPolygon':
        # MultiPolygon structure: [ [[[x, y], [x, y], ...]], [[[x, y], ...]], ... ]
        for polygon in geojson.get('coordinates', []):
            for ring in polygon:
                for coord in ring:
                    coord[0], coord[1] = coord[1], coord[0]
    elif geojson.get('type') == 'Polygon':
        # Polygon structure: [[[x, y], [x, y], ...]]
        for ring in geojson.get('coordinates', []):
            for coord in ring:
                coord[0], coord[1] = coord[1], coord[0]
    elif geojson.get('type') == 'Point':
        # Point structure: [x, y]
        coords = geojson.get('coordinates', [])
        if len(coords) >= 2:
            coords[0], coords[1] = coords[1], coords[0]
    
    return geojson

def upgrade() -> None:
    connection = op.get_bind()
    
    # Get all dams after the target timestamp
    dams = connection.execute(
        sa.text("""
            SELECT d.id, d.border_geometry
            FROM false_positive.dams d
            JOIN false_positive.nodes n ON n.id = d.id
            WHERE n.created_at >= :timestamp
            AND d.border_geometry IS NOT NULL
        """),
        {"timestamp": TARGET_TIMESTAMP}
    ).fetchall()

    # For each dam, flip the coordinates in its border_geometry
    for dam in dams:
        try:
            geojson = dam.border_geometry
            flipped_geojson = flip_coordinates(geojson)
            
            connection.execute(
                sa.text("""
                    UPDATE false_positive.dams
                    SET border_geometry = :geometry
                    WHERE id = CAST(:id AS uuid)
                """),
                {
                    "id": str(dam.id),
                    "geometry": json.dumps(flipped_geojson)
                }
            )
        except Exception as e:
            print(f"Error processing dam {dam.id}: {e}")


def downgrade() -> None:
    # The flip operation is its own inverse, so we can use the same function
    upgrade()
