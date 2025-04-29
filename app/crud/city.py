from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio.session import AsyncSession

import models, schemas


async def create_city(db: AsyncSession, city: schemas.CityCreate) -> dict:
    query = insert(models.City).values(
        name=city.name,
        additional_info=city.additional_info
    )
    result = await db.execute(query)
    await db.commit()
    resp = {**city.model_dump(), "id": result.lastrowid}

    return resp


async def get_all_cities(db: AsyncSession) -> list[schemas.City]:
    query = select(models.City)
    city_list = await db.execute(query)
    return [
        schemas.City.model_validate(city[0]) for city in city_list.fetchall()
    ]
