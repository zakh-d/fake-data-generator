from operator import ge
import random
from abc import ABC
from argparse import ArgumentParser

import yaml
import pandas as pd
from faker import Faker

from schemas import CarType, ParkingStation, User

CAR_TYPES = {
    "opel": ["astra", "insignia"],
    "renault": ["megan", "logan", "duster"],
    "volkswagen": ["golf", "passat", "tiguan"],
    "toyota": ["yaris", "camry", "rav-4"],
}


class ItemGenerator(ABC):
    def __init__(self, fake: Faker, start_index: int = 0) -> None:
        self._fake = fake
        self._curr_idx = start_index

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


generator_mapper = {
    "user": UserGenerator,
    "car_type": CarTypeGenerator,
    "parking_station": ParkingStationGenerator,
}


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="generator.py",
        description="The programs generates fake data for future usage during BI course",
        epilog="",
    )

    parser.add_argument("config_filename")

    args = parser.parse_args()

    with open(args.config_filename, "r") as config_file:
        configuration = yaml.safe_load(config_file)

    fake = Faker("pl_PL")
    
    for key, value in configuration.items():
        
        if key not in generator_mapper:
            continue

        generator: ItemGenerator = generator_mapper[key](fake, start_index=value['start_id'])
        generator.generate_many(value['count']).to_csv(value['output_file'], index=False)
