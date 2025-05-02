from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from dependecies import get_db
import crud.city as crud_city
import schemas


router = APIRouter()


@router.post("/cities/", response_model=schemas.City)
async def create_city(
    city: schemas.CityCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud_city.create_city(db=db, city=city)


@router.get("/cities/", response_model=list[schemas.City])
async def read_cities(db: AsyncSession = Depends(get_db)):
    return await crud_city.get_all_cities(db=db)


@router.get("/cities/{city_id}", response_model=schemas.City)
async def read_single_city(city_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_city.get_single_city(db=db, city_id=city_id)


@router.put("/cities/{city_id}", response_model=schemas.City)
async def city_update(
    city_id: int,
    city: schemas.CityUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await crud_city.update_city(db=db, city_id=city_id, city=city)
