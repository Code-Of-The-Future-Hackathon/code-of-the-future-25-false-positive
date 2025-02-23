import requests

API_BASE_URL = "http://localhost:8000"
CREATE_PLACE_ENDPOINT = f"{API_BASE_URL}/places"

DEFAULT_WATER_PRICE = 1.5
FLOW_PERCENTAGE = 0.1

places_data = [
    {"display_name": "Видин", "latitude": 43.9935, "longitude": 22.8725, "population": 40000, "consumption_per_capita": 0.092},
    {"display_name": "Враца", "latitude": 43.2047, "longitude": 23.5527, "population": 60000, "consumption_per_capita": 0.103},
    {"display_name": "Ловеч", "latitude": 43.1371, "longitude": 24.7141, "population": 30000, "consumption_per_capita": 0.099},
    {"display_name": "Монтана", "latitude": 43.4122, "longitude": 23.2259, "population": 25000, "consumption_per_capita": 0.090},
    {"display_name": "Плевен", "latitude": 43.4188, "longitude": 24.6067, "population": 95000, "consumption_per_capita": 0.100},
    {"display_name": "Велико Търново", "latitude": 43.0757, "longitude": 25.6172, "population": 68000, "consumption_per_capita": 0.105},
    {"display_name": "Габрово", "latitude": 42.8740, "longitude": 25.3199, "population": 50000, "consumption_per_capita": 0.105},
    {"display_name": "Разград", "latitude": 43.5261, "longitude": 26.5241, "population": 30000, "consumption_per_capita": 0.088},
    {"display_name": "Русе", "latitude": 43.8356, "longitude": 25.9657, "population": 148000, "consumption_per_capita": 0.109},
    {"display_name": "Силистра", "latitude": 44.1178, "longitude": 27.2603, "population": 35000, "consumption_per_capita": 0.096},
    {"display_name": "Варна", "latitude": 43.2141, "longitude": 27.9147, "population": 335000, "consumption_per_capita": 0.110},
    {"display_name": "Добрич", "latitude": 43.5666, "longitude": 27.8273, "population": 91000, "consumption_per_capita": 0.096},
    {"display_name": "Търговище", "latitude": 43.2499, "longitude": 26.5723, "population": 37000, "consumption_per_capita": 0.074},
    {"display_name": "Шумен", "latitude": 43.2700, "longitude": 26.9229, "population": 77000, "consumption_per_capita": 0.088},
    {"display_name": "Бургас", "latitude": 42.5048, "longitude": 27.4626, "population": 202000, "consumption_per_capita": 0.115},
    {"display_name": "Сливен", "latitude": 42.6819, "longitude": 26.3221, "population": 89000, "consumption_per_capita": 0.075},
    {"display_name": "Стара Загора", "latitude": 42.4258, "longitude": 25.6345, "population": 138000, "consumption_per_capita": 0.095},
    {"display_name": "Ямбол", "latitude": 42.4848, "longitude": 26.5030, "population": 68000, "consumption_per_capita": 0.091},
    {"display_name": "Благоевград", "latitude": 41.9932, "longitude": 23.4622, "population": 76000, "consumption_per_capita": 0.125},
    {"display_name": "Кюстендил", "latitude": 42.2837, "longitude": 22.6911, "population": 44000, "consumption_per_capita": 0.120},
    {"display_name": "Перник", "latitude": 42.6056, "longitude": 23.0387, "population": 79000, "consumption_per_capita": 0.111},
    {"display_name": "София", "latitude": 42.6977, "longitude": 23.3219, "population": 1200000, "consumption_per_capita": 0.098},
    {"display_name": "София (столица)", "latitude": 42.6977, "longitude": 23.3219, "population": 1300000, "consumption_per_capita": 0.126},
    {"display_name": "Кърджали", "latitude": 41.6518, "longitude": 25.3774, "population": 43000, "consumption_per_capita": 0.081},
    {"display_name": "Пазарджик", "latitude": 42.1928, "longitude": 24.3333, "population": 71000, "consumption_per_capita": 0.115},
    {"display_name": "Пловдив", "latitude": 42.1354, "longitude": 24.7453, "population": 345000, "consumption_per_capita": 0.102},
    {"display_name": "Смолян", "latitude": 41.5748, "longitude": 24.7125, "population": 28000, "consumption_per_capita": 0.084},
    {"display_name": "Хасково", "latitude": 41.9391, "longitude": 25.5632, "population": 75000, "consumption_per_capita": 0.083}
]

def create_place(place_data):
    place_data["water_price"] = DEFAULT_WATER_PRICE
    place_data["non_dam_incoming_flow"] = place_data["consumption_per_capita"] * FLOW_PERCENTAGE
    place_data["radius"] = max(5.0, place_data["population"] / 10000)
    place_data["municipality"] = place_data["display_name"]
    
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(CREATE_PLACE_ENDPOINT, json=place_data, headers=headers)
    
    if response.status_code == 200:
        print(f"Place '{place_data['display_name']}' created successfully.")
    else:
        print(f"Failed to create place '{place_data['display_name']}'")
        print("Status Code:", response.status_code)
        print("Response:", response.json())

for place in places_data:
    create_place(place)

