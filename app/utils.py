from typing import List
import logging

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, update

import models


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO
)


def create_city_temperature_records(
        city_temperature_data: List[dict]
) -> List[dict]:
    return [
        {
            "city_id": city_id,
            "temperature": temperature,
        }
        for city_id, temperature
        in city_temperature_data.items()
    ]


async def insert_new_temperature_records(
        db: AsyncSession,
        new_records: List[dict]
) -> str:
    insert_query = insert(models.Temperature).returning(models.Temperature)
    try:
        await db.execute(insert_query, new_records)
        await db.commit()
    except Exception as e:
        await db.rollback
        logger.error(f"Error inserting temperatures: {e}")
        return

    return f"New temperatures records for {new_records} created."


async def update_existing_temperature_records(
        db: AsyncSession,
        existing_records: List[dict]
) -> str:
    try:
        await db.execute(update(models.Temperature), existing_records)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating temperatures: {e}")
        return

    return f"Updated existing temperature records for {existing_records}."
