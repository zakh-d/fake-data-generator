from typing import Literal, TypedDict
import datetime


class User(TypedDict):
    id: int
    email: str
    first_name: str
    last_name: str


class Car(TypedDict):
    plate_number: str
    car_type_id: int
    station_id: int | Literal[""] | None


class CarType(TypedDict):
    id: int
    model: str
    manufacturer: str
    production_year: int
    price_per_minute: float


class ParkingStation(TypedDict):
    id: int
    latitude: float
    longitude: float
    max_capacity: int


class Rent(TypedDict):
    id: int
    renter: int
    car_plate_number: str
    start_date: datetime.datetime
    end_date: datetime.datetime | None
    start_station_id: int
    end_station_id: int | None


class Invoice(TypedDict):
    number: int
    total_price: float
    description: str
    currency: str
    date: datetime.date
    rent_id: int


class CarTypeExcel(TypedDict):
    id: int
    model: str
    manufacturer: str
    production_year: int
    price: float
    count: int


class ParkingStationExcel(TypedDict):
    id: int
    localization: str
    max_capacity: int
    city: str
