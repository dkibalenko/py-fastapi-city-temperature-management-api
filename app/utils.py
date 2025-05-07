from typing import List

def create_city_temperature_records(
        city_temperature_data: List[dict]
) -> List[dict]:
    return [
        {
            "city_id": city_id,
            "temperature": temperature,
        }
        for city_id, temperature in city_temperature_data.items()
    ]
