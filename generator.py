from argparse import ArgumentParser
from collections import deque
import datetime

import yaml
from faker import Faker

from item_generators import (
    CarGenerator,
    CarTypeGenerator,
    ItemGenerator,
    ParkingStationGenerator,
    RentGenerator,
    UserGenerator,
)

generator_mapper = {
    "user": UserGenerator,
    "car_type": CarTypeGenerator,
    "parking_station": ParkingStationGenerator,
    "car": CarGenerator,
    "rent": RentGenerator,
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

    generated_values = {}
    generation_queue = deque(configuration.keys())

    while len(generation_queue) > 0:
        key = generation_queue.popleft()
        value = configuration[key]

        if key not in generator_mapper:
            continue

        kwargs = {}
        if "depends_on" in value:
            has_all_nessesary_data = True
            for dependency in value["depends_on"]:
                if dependency not in generated_values:
                    generation_queue.append(key)
                    has_all_nessesary_data = False
                    break

            if not has_all_nessesary_data:
                continue

            kwargs["dependencies"] = {
                d: generated_values[d] for d in value["depends_on"]
            }

        if "start_period" in value:
            kwargs["start_period"] = datetime.datetime.strptime(
                value["start_period"], "%d/%m/%Y %H:%M"
            )

        if "end_period" in value:
            kwargs["end_period"] = datetime.datetime.strptime(
                value["end_period"], "%d/%m/%Y %H:%M"
            )

        generator: ItemGenerator = generator_mapper[key](
            fake, start_index=value["start_id"], **kwargs
        )

        generated_values[key] = generator.generate_many(value["count"])
        generated_values[key].to_csv(value["output_file"], index=False)
