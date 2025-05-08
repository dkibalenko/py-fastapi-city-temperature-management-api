from sqlalchemy import select, insert, update
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


async def get_all_cities(db: AsyncSession) -> list[models.City]:
    result = await db.execute(select(models.City))
    return result.scalars().all()


async def get_single_city(db: AsyncSession, city_id: int) -> models.City:
    query = select(models.City).where(models.City.id == city_id)
    result = await db.execute(query)
    return result.scalar()


async def update_city(
        db: AsyncSession,
        city_id: int,
        city: schemas.CityUpdate
) -> schemas.City:
    city_being_updated = await db.get(entity=models.City, ident=city_id)

    if not city_being_updated:
        raise HTTPException(
            status_code=404,
            detail=f"City with id {city_id} not found."
        )

    update_data = city.model_dump(exclude_unset=True)

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
