from pydantic import BaseModel, ConfigDict


class CityBase(BaseModel):
    name: str
    additional_info: str


class CityCreate(CityBase):
    pass


class CityUpdate(CityBase):
    pass


class CityDelete(BaseModel):
    message: str


class City(CityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
