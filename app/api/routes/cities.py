from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from dependecies import get_db
from crud.city import create_city
import schemas


router = APIRouter()


@router.post("/cities/", response_model=schemas.City)
async def cities(city: schemas.CityCreate, db: AsyncSession = Depends(get_db)):
    return await create_city(db=db, city=city)
