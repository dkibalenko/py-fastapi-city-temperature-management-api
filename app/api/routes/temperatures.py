from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio.session import AsyncSession

from dependecies import get_db
import crud.temperature as crud_temperature
import schemas


router = APIRouter()


@router.post("/temperatures/update/", response_model=schemas.TemperatureUpdate)
async def update_cities_temperatures(db: AsyncSession = Depends(get_db)):
    return await crud_temperature.update_temperatures(db=db)


@router.get("/temperatures/", response_model=List[schemas.Temperature])
async def read_temperatures(
    db: AsyncSession = Depends(get_db),
    city_id: int = Query(None)
):
    temperatures = await crud_temperature.get_all_temperatures(
        db=db,
        city_id=city_id
    )

    if not temperatures:
        raise HTTPException(
            status_code=404,
            detail="No temperatures found."
        )

    return temperatures


@router.get("/temperture/{temp_id}/", response_model=schemas.Temperature)
async def read_single_temperature(
    temp_id: int,
    db: AsyncSession = Depends(get_db)
):
    temperature = await crud_temperature.read_single_temperature_record(
        db=db,
        temp_id=temp_id
    )

    if not temperature:
        raise HTTPException(
            status_code=404,
            detail=f"Temperature with id {temp_id} not found."
        )

    return temperature
