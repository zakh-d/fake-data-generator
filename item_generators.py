import datetime
import random
from abc import ABC
from collections import deque

import pandas as pd
from faker import Faker

from schemas import (
    Car,
    CarOnStation,
    CarType,
    CarTypeExcel,
    Invoice,
    ParkingStation,
    ParkingStationExcel,
    Rent,
    User,
)

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
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
        modification_probability: float = 0.0,
        supports_modification: bool = False,
    ) -> None:
        self._fake = fake
        self._curr_idx = start_id
        self._dependencies = dependencies
        self._start_period = start_period
        self._end_period = end_period
        self._modification_probability = modification_probability
        self.supports_modification = supports_modification

    def _get_curr_idx_and_update(self) -> int:
        self._curr_idx += 1
        return self._curr_idx - 1

    def generate(self) -> object:
        raise NotImplementedError()

    def modify(self, original):
        raise NotImplementedError()

    def generate_many(self, n: int) -> pd.DataFrame:
        items = []
        for _ in range(n):
            items.append(self.generate())
        return pd.DataFrame(items)

    def _modify_helper(self, row: pd.Series) -> pd.Series:
        if random.random() < self._modification_probability:
            modified_row = self.modify(row)
        else:
            modified_row = row
        for col, new_value in modified_row.items():
            row[col] = new_value
        return row

    def modify_many(self, original: pd.DataFrame) -> pd.DataFrame:
        return original.apply(self._modify_helper, axis=1)


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
    def __init__(
        self,
        fake: Faker,
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
        modification_probability: float = 0,
    ) -> None:
        super().__init__(
            fake,
            start_id,
            dependencies,
            start_period,
            end_period,
            modification_probability,
            supports_modification=True,
        )

    def modify(self, original: ParkingStation) -> ParkingStation:
        copied = original.copy()
        copied["max_capacity"] += random.randint(-2, 3)
        return copied

    def modify_many(self, original: pd.DataFrame) -> pd.DataFrame:
        modified = super().modify_many(original)
        return modified.astype({"max_capacity": "int32", "id": "int32"})

    def generate(self) -> ParkingStation:
        id_ = self._get_curr_idx_and_update()
        latitude = float(self._fake.latitude())
        longitude = float(self._fake.longitude())
        max_capacity = random.randint(5, 11)

        return {
            "id": id_,
            "latitude": latitude,
            "longitude": longitude,
            "max_capacity": max_capacity,
        }


class CarTypeGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
        modification_probability: float = 0,
    ) -> None:
        super().__init__(
            fake,
            start_id,
            dependencies,
            start_period,
            end_period,
            modification_probability,
            supports_modification=True,
        )

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

    def modify(self, original: CarType) -> CarType:
        return {
            **original,
            "id": self._get_curr_idx_and_update(),
            "price_per_minute": random.random() * 10,
        }


class CarGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
    ) -> None:
        super().__init__(
            fake,
            start_id,
            dependencies,
            start_period,
            end_period,
            0,
            supports_modification=False,
        )
        if "car_type" not in self._dependencies:
            raise RuntimeError("car_types dependency was't provided")

        self._car_type_ids = list(self._dependencies["car_type"]["id"])

    def generate(self) -> Car:
        return {
            "plate_number": self._fake.license_plate(),
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
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
        modification_probability: float = 0,
    ) -> None:
        super().__init__(
            fake,
            start_id,
            dependencies,
            start_period,
            end_period,
            modification_probability,
        )

        if "car" not in self._dependencies:
            raise RuntimeError("car dependency was't provided")

        if "parking_station" not in self._dependencies:
            raise RuntimeError("parking_station dependency was't provided")

        if "user" not in self._dependencies:
            raise RuntimeError("user dependency was't provided")

        self._user_ids = list(dependencies["user"]["id"])
        self._parking_station_ids = list(dependencies["parking_station"]["id"])
        self._car_numbers = list(dependencies["car"]["plate_number"])

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
            "car_plate_number": random.choice(self._car_numbers),
        }


class InvoiceGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
        modification_probability: float = 0,
    ) -> None:
        super().__init__(
            fake,
            start_id,
            dependencies,
            start_period,
            end_period,
            modification_probability,
        )

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


class CarTypeExcelGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
        modification_probability: float = 0,
    ) -> None:
        super().__init__(
            fake,
            start_id,
            dependencies,
            start_period,
            end_period,
            modification_probability,
        )

        if "car" not in dependencies:
            raise RuntimeError("car dependency wasn't added")

        if "car_type" not in dependencies:
            raise RuntimeError("car_type dependency wasn't added")

        self._car_types = deque(dependencies["car_type"].to_dict("records"))
        self._car_types_count = self._parse_car_types_count()

    def _parse_car_types_count(self) -> dict[int, int]:
        car_type_counts = {}
        for _, car in self._dependencies["car"].iterrows():
            if car["car_type_id"] in car_type_counts:
                car_type_counts[car["car_type_id"]] += 1
            else:
                car_type_counts[car["car_type_id"]] = 1
        return car_type_counts

    def _get_next_car_type(self) -> CarType:
        car_type = self._car_types.pop()
        return {
            "id": car_type["id"],
            "model": car_type["model"],
            "manufacturer": car_type["manufacturer"],
            "production_year": car_type["production_year"],
            "price_per_minute": car_type["price_per_minute"],
        }

    def generate(self) -> CarTypeExcel:
        car_type = self._get_next_car_type()
        return {
            "id": car_type["id"],
            "model": car_type["model"],
            "manufacturer": car_type["manufacturer"],
            "production_year": car_type["production_year"],
            "price": random.randint(60_000, 150_000),
            "count": self._car_types_count.get(car_type["id"], 0),
        }


class ParkingStationExcelGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
        modification_probability: float = 0,
    ) -> None:
        super().__init__(
            fake,
            start_id,
            dependencies,
            start_period,
            end_period,
            modification_probability,
        )

        if "parking_station" not in dependencies:
            raise RuntimeError("parking_station dependency wasn't added")

        self._parking_stations = deque(
            dependencies["parking_station"].to_dict("records")
        )

    def _get_next_parking_station(self) -> ParkingStation:
        station = self._parking_stations.pop()

        return {
            "id": station["id"],
            "latitude": station["latitude"],
            "longitude": station["longitude"],
            "max_capacity": station["max_capacity"],
        }

    def generate(self) -> ParkingStationExcel:
        station = self._get_next_parking_station()
        city = self._fake.city()
        return {
            "id": station["id"],
            "max_capacity": station["max_capacity"],
            "city": city,
            "localization": f"{city}, near żabka",
        }


class CarsOnStationGenerator(ItemGenerator):
    def __init__(
        self,
        fake: Faker,
        start_id: int = 0,
        dependencies: dict[str, pd.DataFrame] = {},
        start_period: datetime.datetime = datetime.datetime.min,
        end_period: datetime.datetime = datetime.datetime.max,
    ) -> None:
        super().__init__(
            fake,
            start_id,
            dependencies,
            start_period,
            end_period,
            0,
            supports_modification=False,
        )

        if "car" not in self._dependencies:
            raise RuntimeError("car dependency was not provided")

        if "parking_station" not in self._dependencies:
            raise RuntimeError("parking_station dependency was not provided")
        self._parking_station_ids = list(dependencies["parking_station"]["id"])
        self._car_numbers = list(dependencies["car"]["plate_number"])

    def generate(self) -> CarOnStation:
        random_datetime = random_date(self._start_period, self._end_period)
        return {
            "id": self._get_curr_idx_and_update(),
            "start_time": random_datetime,
            "end_time": random_datetime
            + datetime.timedelta(minutes=random.randint(10, 300)),
            "car_plate_number": random.choice(self._car_numbers),
            "parking_station_id": random.choice(self._parking_station_ids),
        }
