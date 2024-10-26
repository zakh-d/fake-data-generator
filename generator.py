import random
from abc import ABC
from argparse import ArgumentParser

import yaml
import pandas as pd
from faker import Faker

from schemas import CarType, User

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

    def generate(self) -> object:
        raise NotImplementedError()

    def generate_many(self, n: int) -> pd.DataFrame:
        items = []
        for _ in range(n):
            items.append(self.generate())
        return pd.DataFrame(items)


class UserGenerator(ItemGenerator):
    def generate(self) -> User:
        id_ = self._curr_idx
        self._curr_idx += 1
        email = self._fake.email()
        first_name = self._fake.first_name()
        last_name = self._fake.last_name()
        return {
            "id": id_,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }


class CarTypeGenerator(ItemGenerator):
    def generate(self) -> CarType:
        id_ = self._curr_idx
        self._curr_idx += 1
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


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="generator.py",
        description="The programs generates fake data for future usage during BI course",
        epilog="",
    )

    parser.add_argument('config_filename')
    

    args = parser.parse_args()
    
    with open(args.config_filename, 'r') as config_file:
        configuration = yaml.safe_load(config_file)
    
    fake = Faker('pl_PL')

    user_generator = UserGenerator(fake, start_index=configuration['user']['start_id'])
    car_type_generator = CarTypeGenerator(fake, start_index=configuration['car_type']['start_id'])

    user_generator.generate_many(configuration['user']['count']).to_csv(configuration['user']['output_file'])
    car_type_generator.generate_many(configuration['car_type']['count']).to_csv(configuration['car_type']['output_file'])
