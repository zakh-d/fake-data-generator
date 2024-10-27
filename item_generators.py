import random
from abc import ABC

import pandas as pd
from faker import Faker

from schemas import Car, CarType, ParkingStation, User

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
    ) -> None:
        self._fake = fake
        self._curr_idx = start_index
        self._dependencies = dependencies

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
    ) -> None:
        super().__init__(fake, start_index, dependencies)

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
