from argparse import ArgumentParser
from collections import deque

import yaml
from faker import Faker

from item_generators import (
    CarGenerator,
    CarTypeGenerator,
    ItemGenerator,
    ParkingStationGenerator,
    UserGenerator,
)

generator_mapper = {
    "user": UserGenerator,
    "car_type": CarTypeGenerator,
    "parking_station": ParkingStationGenerator,
    "car": CarGenerator,
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

        if "depends_on" in value:
            for dependency in value["depends_on"]:
                if dependency not in generated_values:
                    generation_queue.append(key)
                    continue

        dependencies = {d: generated_values[d] for d in value.get("depends_on", [])}

        generator: ItemGenerator = generator_mapper[key](
            fake, start_index=value["start_id"], dependencies=dependencies
        )

        generated_values[key] = generator.generate_many(value["count"])
        generated_values[key].to_csv(value["output_file"], index=False)
