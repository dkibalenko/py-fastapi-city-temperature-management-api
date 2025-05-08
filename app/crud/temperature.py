from datetime import datetime
import pdb
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import ValidationError

from services.weather_fetcher import read_temperature_api
import schemas, models
import utils


async def construct_temperature_records(db: AsyncSession) -> List[dict]:
    """
    Construct a list of temperature records for cities from the database.
    """
    db_city_records = await db.execute(select(models.City))
    db_city_objects = [
        city_record
        for city_record
        in db_city_records.scalars().all()
    ]

    temperature_api_data = await read_temperature_api(cities=db_city_objects)

    return utils.create_city_temperature_records(
        temperature_api_data
    )


async def map_temperature_city_id_to_temperature_id(
        db: AsyncSession
) -> dict[models.Temperature.city_id: models.Temperature.id]:
    """
    Maps temperature city_id to its corresponding temperature id.
    """
    db_temperature_records = await db.execute(select(models.Temperature))
    return {
        temperature_record.city_id: temperature_record.id
        for temperature_record in db_temperature_records.scalars().all()
    }


async def update_temperatures(db: AsyncSession) -> schemas.TemperatureUpdate:
    """
    Updates temperature records for cities in the database.

    This function constructs temperature records for all cities, inserts new 
    temperature records for cities not already in the database, and updates 
    existing records with the latest temperature data.
    """

    temperature_records = await construct_temperature_records(db=db)
    db_temperature_city_ids = await map_temperature_city_id_to_temperature_id(
        db=db
    )

    new_records = [
        {**temperature_record, "date_time": datetime.now()}
        for temperature_record in temperature_records
        if temperature_record["city_id"] not in db_temperature_city_ids
    ]

    if new_records:
        insert_result = await utils.insert_new_temperature_records(
            db=db,
            new_records=new_records
        )
        utils.logger.info(insert_result)

    existing_records = [
        {
            "id": db_temperature_city_ids[temperature_record["city_id"]],
            "date_time": datetime.now(),
            "temperature": temperature_record["temperature"]
        }
        for temperature_record in temperature_records
        if temperature_record["city_id"] in db_temperature_city_ids
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


async def get_all_temperatures(db: AsyncSession) -> List[schemas.Temperature]:
    """
    Retrieves a list of all temperature records from the database.

    The function constructs a query to get all temperature records from the
    database, and then validates each record using pydantic.
    """
    query = (
        select(models.Temperature)
        .options(selectinload(models.Temperature.city))
    )
    temperature_list = await db.execute(query)
    temperatures = []
    for temperature in temperature_list.scalars().all():
        try:
            obj = schemas.Temperature.model_validate(temperature)
        except ValidationError as exc:
            utils.logger.error(
                f"Error during validation {temperature} object, details: {exc}"
            )
            continue
        temperatures.append(obj)

    return temperatures


async def read_single_temperature_record(
    db: AsyncSession,
    temp_id: int
) -> models.Temperature:
    temperature_record = await db.get(
        entity=models.Temperature,
        ident=temp_id,
        options=(selectinload(models.Temperature.city),)
    )

    return temperature_record
