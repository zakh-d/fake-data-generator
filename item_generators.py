from collections import deque
import datetime
import random
from abc import ABC

import pandas as pd
from faker import Faker

from schemas import Car, CarType, Invoice, ParkingStation, Rent, User

CAR_TYPES = {
    "opel": ["astra", "insignia"],
    "renault": ["megan", "logan", "duster"],
    "volkswagen": ["golf", "passat", "tiguan"],
    "toyota": ["yaris", "camry", "rav-4"],
}


class ItemGenerator(ABC):
    def __init__(
        self,
        fake: Faker,
        start_index: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
    ) -> None:
        self._fake = fake
        self._curr_idx = start_index
        self._dependencies = dependencies
        self._start_period = start_period
        self._end_period = end_period

    def _get_curr_idx_and_update(self) -> int:
        self._curr_idx += 1
        return self._curr_idx - 1

    def generate(self) -> object:
        raise NotImplementedError()

    def generate_many(self, n: int) -> pd.DataFrame:
        items = []
        for _ in range(n):
            items.append(self.generate())
        return pd.DataFrame(items)


class UserGenerator(ItemGenerator):
    def generate(self) -> User:
        id_ = self._get_curr_idx_and_update()
        email = self._fake.email()
        first_name = self._fake.first_name()
        last_name = self._fake.last_name()
        return {
            "id": id_,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }


class ParkingStationGenerator(ItemGenerator):
    def generate(self) -> ParkingStation:
        id_ = self._get_curr_idx_and_update()
        latitude = random.random()
        longitude = random.random()
        max_capacity = random.randint(5, 11)

        return {
            "id": id_,
            "latitude": latitude,
            "longitude": longitude,
            "max_capacity": max_capacity,
        }


class CarTypeGenerator(ItemGenerator):
    def generate(self) -> CarType:
        id_ = self._get_curr_idx_and_update()
        manufacturer = random.choice(list(CAR_TYPES.keys()))
        model = random.choice(CAR_TYPES[manufacturer])
        year = random.randint(2000, 2020)
        price_per_minute = random.random() * 10
        return {
            "id": id_,
            "model": model,
            "manufacturer": manufacturer,
            "production_year": year,
            "price_per_minute": price_per_minute,
        }


PLATE_REGIONS = ["GD", "GDA", "GDY", "GSP"]


class CarGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_index: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
    ) -> None:
        super().__init__(fake, start_index, dependencies, start_period, end_period)
        if "car_type" not in self._dependencies:
            raise RuntimeError("car_types dependency was't provided")

        if "parking_station" not in self._dependencies:
            raise RuntimeError("car_types dependency was't provided")

        self._car_type_ids = list(self._dependencies["car_type"]["id"])
        self._parking_station_ids = list(self._dependencies["parking_station"]["id"])

    def generate(self) -> Car:
        station_id = None
        if random.random() < 0.3:
            station_id = random.choice(self._parking_station_ids)

        return {
            "plate_number": random.choice(PLATE_REGIONS)
            + str(random.randint(10000, 99999)),
            "station_id": station_id,
            "car_type_id": random.choice(self._car_type_ids),
        }


def random_date(start: datetime.datetime, end: datetime.datetime) -> datetime.datetime:
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)


class RentGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_index: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
    ) -> None:
        super().__init__(fake, start_index, dependencies, start_period, end_period)

        if "car" not in self._dependencies:
            raise RuntimeError("car dependency was't provided")

        if "parking_station" not in self._dependencies:
            raise RuntimeError("parking_station dependency was't provided")

        if "user" not in self._dependencies:
            raise RuntimeError("user dependency was't provided")

        self._user_ids = list(dependencies["user"]["id"])
        self._parking_station_ids = list(dependencies["parking_station"]["id"])
        self._car_plates = list(dependencies["car"]["plate_number"])

    def generate(self) -> Rent:
        start_date = random_date(self._start_period, self._end_period)
        rent_time = datetime.timedelta(minutes=random.randint(5, 300))
        end_date = start_date + rent_time
        return {
            "id": self._get_curr_idx_and_update(),
            "renter": random.choice(self._user_ids),
            "start_station_id": random.choice(self._parking_station_ids),
            "start_date": start_date,
            "end_station_id": random.choice(self._parking_station_ids),
            "end_date": end_date,
            "car_plate_number": random.choice(self._car_plates),
        }


class InvoiceGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_index: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
    ) -> None:
        super().__init__(fake, start_index, dependencies, start_period, end_period)

        if "rent" not in self._dependencies:
            raise RuntimeError("rent dependency wasn't provided")
        self._rents_left = deque(dependencies["rent"].to_dict("records"))

    def _get_next_rent(self) -> Rent:
        rent = self._rents_left.pop()
        return {
            "id": rent["id"],
            "renter": rent["renter"],
            "start_station_id": rent["start_station_id"],
            "start_date": rent["start_date"],
            "end_station_id": rent["end_station_id"],
            "end_date": rent["end_date"],
            "car_plate_number": rent["car_plate_number"],
        }

    def generate(self) -> Invoice:
        rent = self._get_next_rent()
        rent_time_in_minutes = 30
        if rent["end_date"] is not None:
            delta = rent["end_date"] - rent["start_date"]
            rent_time_in_minutes = delta.seconds / 60
        return {
            "number": self._get_curr_idx_and_update(),
            "rent_id": rent["id"],
            "date": rent["start_date"].date(),
            "currency": "pln",
            "total_price": rent_time_in_minutes * random.random() * 10,
            "description": f'Car Renting for {rent["start_date"].date()}',
        }