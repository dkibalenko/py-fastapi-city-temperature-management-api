from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from dependecies import get_db
import crud.temperature as crud_temperature
import schemas


router = APIRouter()


@router.post("/temperatures/update/", response_model=schemas.TemperatureUpdate)
async def update_cities_temperatures(db: AsyncSession = Depends(get_db)):
    return await crud_temperature.update_temperatures(db=db)
