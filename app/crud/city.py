from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

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


async def get_single_city(db: AsyncSession, city_id: int) -> schemas.City:
    query = select(models.City).where(models.City.id == city_id)
    db_city = await db.execute(query)
    city = db_city.scalar()

    if not city:
        raise HTTPException(
            status_code=404,
            detail=f"City with id {city_id} not found."
        )

    return schemas.City.model_validate(city)
