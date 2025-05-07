from typing import List
import httpx

import models


OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
OPEN_WEATHER_API_KEY = "71770e6cab8b6948bb9da995938060fa"


async def read_temperature_api(cities: List[models.City]):
    temperatures = {}

    async with httpx.AsyncClient() as client:
        for city in cities:
            try:
                resp = await client.get(
                    OPEN_WEATHER_URL,
                    params={
                        "q": city.name,
                        "appid": OPEN_WEATHER_API_KEY,
                        "units": "metric"
                    }
                )
                resp.raise_for_status()
            except httpx.HTTPError as e:
                print(f"HTTP error: {e}")
                print(f"City not found: {city.name}")
                continue
            except httpx.TimeoutException:
                print("Timeout error")
            except httpx.ConnectError:
                print("Connection error")
            except httpx.ReadError:
                print("Read error")

            city_temperature = resp.json()["main"]["temp"]
            temperatures[city.id] = city_temperature

    return temperatures
