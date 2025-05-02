from sqlalchemy import select, insert, update, delete
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
    result = await db.execute(query)
    city = result.scalar()

    if not city:
        raise HTTPException(
            status_code=404,
            detail=f"City with id {city_id} not found."
        )

    return schemas.City.model_validate(city)


async def update_city(
        db: AsyncSession,
        city_id: int,
        city: schemas.CityUpdate
) -> schemas.City:
    # query = select(models.City).where(models.City.id == city_id)
    # result = await db.execute(query)
    # city_being_updated = result.scalar()
    city_being_updated = await db.get(entity=models.City, ident=city_id)  # efficient for retrieving single objects by primary key.

    if not city_being_updated:
        raise HTTPException(
            status_code=404,
            detail=f"City with id {city_id} not found."
        )

    update_data = city.model_dump(exclude_unset=True)  # exclude_unset: Whether to exclude fields that have not been explicitly set.

    # for key, value in update_data.items():
    #     setattr(city_being_updated, key, value)
    update_query = (
        update(models.City)
        .where(models.City.id == city_id)
        .values(**update_data)
    )

    await db.execute(update_query)
    await db.commit()
    await db.refresh(city_being_updated)

    return city_being_updated


async def remove_city(db: AsyncSession, city_id: int) -> schemas.CityDelete:
    city_being_deleted = await db.get(entity=models.City, ident=city_id)

    if not city_being_deleted:
        raise HTTPException(
            status_code=404,
            detail=f"City with id {city_id} not found."
        )

    await db.delete(city_being_deleted)
    await db.commit()

    return schemas.CityDelete(message=f"The city with id {city_id} is deleted")
