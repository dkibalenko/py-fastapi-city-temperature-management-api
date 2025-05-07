from datetime import datetime
import pdb

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, update, select
from fastapi import HTTPException

from services.weather_fetcher import read_temperature_api
import schemas, models
from utils import create_city_temperature_records


async def update_temperatures(db: AsyncSession) -> schemas.TemperatureUpdate:
    db_city_records = await db.execute(select(models.City))
    db_city_objects = [
        city_record[0]
        for city_record in db_city_records.fetchall()
    ]

    temperature_api_data = await read_temperature_api(cities=db_city_objects)

    new_temperature_records = create_city_temperature_records(
        temperature_api_data
    )

    db_temperature_records = await db.execute(select(models.Temperature))
    db_temperature_city_ids = {
        temperature_record[0].city_id: temperature_record[0].id
        for temperature_record
        in db_temperature_records.fetchall()
    }

    new_records = [
        {**record, "date_time": datetime.now()}
        for record in new_temperature_records
        if record["city_id"] not in db_temperature_city_ids
    ]

    if new_records:
        insert_query = insert(models.Temperature).returning(models.Temperature)
        try:
            await db.execute(insert_query, new_records)
            await db.commit()
        except Exception as e:
            await db.rollback
            print(f"Error inserting temperatures: {e}")

    existing_records = [
        {
            "id": db_temperature_city_ids[record["city_id"]],
            "date_time": datetime.now(),
            "temperature": record["temperature"]
        }
        for record in new_temperature_records
        if record["city_id"] in db_temperature_city_ids
    ]

    if existing_records:
        try:
            await db.execute(update(models.Temperature), existing_records)
            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"Error updating temperatures: {e}")

    return schemas.TemperatureUpdate(
        message="Temperatures for all cities updated."
    )
