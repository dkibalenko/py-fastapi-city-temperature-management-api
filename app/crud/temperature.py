from datetime import datetime
import pdb

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from services.weather_fetcher import read_temperature_api
import schemas, models
import utils


async def update_temperatures(db: AsyncSession) -> schemas.TemperatureUpdate:
    db_city_records = await db.execute(select(models.City))
    db_city_objects = [
        city_record[0]
        for city_record in db_city_records.fetchall()
    ]

    temperature_api_data = await read_temperature_api(cities=db_city_objects)

    new_temperature_records = utils.create_city_temperature_records(
        temperature_api_data
    )

    db_temperature_records = await db.execute(select(models.Temperature))
    db_temperature_city_ids = {
        temperature_record[0].city_id: temperature_record[0].id
        for temperature_record in db_temperature_records.fetchall()
    }

    new_records = [
        {**record, "date_time": datetime.now()}
        for record in new_temperature_records
        if record["city_id"] not in db_temperature_city_ids
    ]

    if new_records:
        insert_result = await utils.insert_new_temperature_records(
            db=db,
            new_records=new_records
        )
        utils.logger.info(insert_result)

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
        update_result = await utils.update_existing_temperature_records(
            db=db,
            existing_records=existing_records
        )
        utils.logger.info(update_result)

    return schemas.TemperatureUpdate(
        message="Temperatures for cities updated."
    )
