from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from dependecies import get_db
from crud.city import create_city, get_all_cities, get_single_city
import schemas


router = APIRouter()


@router.post("/cities/", response_model=schemas.City)
async def cities(city: schemas.CityCreate, db: AsyncSession = Depends(get_db)):
    return await create_city(db=db, city=city)


@router.get("/cities/", response_model=list[schemas.City])
async def cities(db: AsyncSession = Depends(get_db)):
    return await get_all_cities(db=db)


@router.get("/cities/{city_id}", response_model=schemas.City)
async def cities(city_id: int, db: AsyncSession = Depends(get_db)):
    return await get_single_city(db=db, city_id=city_id)
