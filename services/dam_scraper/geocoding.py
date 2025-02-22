import requests
import os
import urllib.parse
from typing import Dict, Tuple, List
from caching import cache_response_forever_in_fs


class GeocodingError(Exception):
    pass


def _bounds_to_polygon(bounds: Dict[str, Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Convert boundary coordinates to a polygon (rectangle) of coordinates.
    The polygon is returned as a list of (lat, lng) coordinates in clockwise order,
    starting from the northeast corner.
    """
    ne = bounds['northeast']
    sw = bounds['southwest']
    nw = (bounds['northeast'][0], bounds['southwest'][1])  # (ne_lat, sw_lng)
    se = (bounds['southwest'][0], bounds['northeast'][1])  # (sw_lat, ne_lng)
    
    # Return coordinates in clockwise order, closing the polygon by repeating the first point
    return [ne, se, sw, nw, ne]


@cache_response_forever_in_fs
def geocode_location_opencage(location_name: str) -> Dict:
    urlencoded_location_name = urllib.parse.quote(location_name)
    response = requests.get(f"https://api.opencagedata.com/geocode/v1/json?q={urlencoded_location_name}&key={os.getenv('OPENCAGE_API_KEY')}")
    
    if not response.ok:
        raise GeocodingError(f"API request failed with status code {response.status_code}")
        
    data = response.json()
    
    if data['status']['code'] != 200:
        raise GeocodingError(f"API returned error status: {data['status']['message']}")
        
    if not data['results']:
        raise GeocodingError(f"No coordinates found for location: {location_name}")
        
    result = data['results'][0]
    
    if 'bounds' not in result:
        raise GeocodingError(f"No boundary information available for location: {location_name}")
    
    bounds = {
        'northeast': (result['bounds']['northeast']['lat'], result['bounds']['northeast']['lng']),
        'southwest': (result['bounds']['southwest']['lat'], result['bounds']['southwest']['lng'])
    }
    
    return {
        'center': (result['geometry']['lat'], result['geometry']['lng']),
        'polygon': _bounds_to_polygon(bounds)
    }

