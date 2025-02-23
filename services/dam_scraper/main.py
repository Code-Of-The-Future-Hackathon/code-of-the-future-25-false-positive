import os
import requests
from dam_registry_joomla_client import get_all_municipalities, get_dams_for_municipality
import geocoding
import json
from dotenv import load_dotenv

load_dotenv()

DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://localhost:8000")


def _create_dam(dam_data):
    response = requests.post(f"{DATA_SERVICE_URL}/dams", json=dam_data)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    municipalities = get_all_municipalities()
    print(len(municipalities))
    
    for municipality in municipalities[:1]:
        dams = get_dams_for_municipality(municipality['id'])
        if dams:
            print(f"Found {len(dams)} dams for municipality {municipality['name']}")
            for dam in dams:
                from supported_dams import SUPPORTED_DAMS

                # Skip dams that don't match our supported list
                if not any(supported_name.lower() in dam['name'].lower() or dam['name'].lower() in supported_name.lower() for supported_name in SUPPORTED_DAMS):
                    print(f"Skipping unsupported dam {dam['name']}")
                    continue

                try:
                    location_data = geocoding.geocode_location_opencage(dam['location'].replace('яз.', 'Язовир') + ' България')
                    geojson_coords = [[[
                        [point[1], point[0]]  # GeoJSON uses [longitude, latitude] order
                        for point in location_data['polygon']
                    ]]]
                    
                    _create_dam({
                        'display_name': dam['name'],
                        'latitude': location_data['center'][0],
                        'longitude': location_data['center'][1],
                        'border_geometry': {
                            "type": "MultiPolygon",
                            "coordinates": geojson_coords
                        },
                        'max_volume': 0,
                        'description': json.dumps({'ТОВА Е ОТ БОЖО ЗА ПО-КЪСНА УПОТРЕБА': True, 'dam': dam, 'location_data': location_data}),
                        'owner': dam['owner'],
                        'owner_contact': 'redacted@false-positive.dev',
                        'operator': dam['operator'],
                        'operator_contact': 'redacted@false-positive.dev',
                        'sku': dam['sku'],
                        'place_ids': [],
                    })
                except geocoding.GeocodingError as e:
                    print(f"Failed to geocode dam {dam['name']}: {e}")
                    continue
    
