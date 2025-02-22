import requests
from bs4 import BeautifulSoup
import json
from caching import cache_response_forever_in_fs

@cache_response_forever_in_fs
def clean_title(html_title):
    """Extract clean dam name from HTML title"""
    soup = BeautifulSoup(html_title, 'html.parser')
    return soup.get_text().strip()


DAM_REGISTRY_URL = "https://dams.damtn.government.bg/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://dams.damtn.government.bg/'
}


@cache_response_forever_in_fs
def get_dams_for_municipality(municipality_id: str):
    """Get all dams for a given municipality ID."""
    querystring = {
        "formdata[title]": "",
        "formdata[oblast]": "-1",
        "formdata[obstina]": municipality_id,
        "Itemid": "107",
        "option": "com_webregister",
        "view": "items",
        "tmpl": "none",
        "format": "json",
        "lang": "en",
        "page": "-1",
        "formdata[searchType]": "item",
        "task": "items.getItems"
    }

    response = requests.get(DAM_REGISTRY_URL, params=querystring, headers=HEADERS, verify=False)
    data = response.json()
    
    if 'data' not in data:
        return []
            
    # Extract and clean the data
    dams = []
    for dam_id, dam_data in data['data'].items():
        dam = {
            'damtn_id': dam_id,
            'name': clean_title(dam_data['title']),
            'municipality': dam_data['item_field_f0001'],  # Община
            'district': dam_data['item_field_f0002'],      # Област
            'location': dam_data['item_field_f0003'],      # Населено място
            'operator': dam_data['operatorName'],
            'owner': dam_data['ownerName'],
            'sku': dam_data['sku']
        }
        dams.append(dam)

    # Sort by location and name
    dams.sort(key=lambda x: (x['location'], x['name']))
    return dams


@cache_response_forever_in_fs
def get_all_municipalities():
    """Get all municipalities from the registry."""
    # Get the main page
    response = requests.get(DAM_REGISTRY_URL, headers=HEADERS, verify=False)
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the municipality select element
    select = soup.find('select', {'name': 'formdata[obstina]'})
    if not select:
        return []
    
    # Extract municipalities
    municipalities = []
    for option in select.find_all('option'):
        if option.get('value') != '-1':  # Skip the "All municipalities" option
            municipalities.append({
                'id': option.get('value'),
                'name': option.text.strip()
            })
    return municipalities
