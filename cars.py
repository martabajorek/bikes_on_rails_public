import json
from datetime import datetime
from typing import Any

from api import send_query_get

def compact_datetime(value: str) -> str:
    return datetime.fromisoformat(value).strftime("%Y%m%d%H%M")


def build_cars_endpoint(
    connection: dict[str, Any],
    station_from: dict[str, Any],
    station_to: dict[str, Any],
) -> str:
    return (
        "https://api-gateway.intercity.pl/grm/sklad/wbnet/"
        f"{connection['kategoriaPociagu']}/{connection['nrPociagu']}/"
        f"{compact_datetime(connection['dataPrzyjazdu'])}/"
        f"{station_from['kodEPA']}/"
        f"{compact_datetime(connection['dataWyjazdu'])}/"
        f"{station_to['kodEPA']}"
    )


def find_bike_cars(data: dict[str, Any]) -> list[dict[str, str | None]]:
    car_amenities = data.get("wagonyUdogodnienia", {})
    car_schemas = data.get("wagonySchemat", {})

    return [
        {
            "wagon": car_number,
            "wagonySchemat": car_schemas.get(car_number),
        }
        for car_number, amenities in car_amenities.items()
        if "309" in amenities
    ]


def main() -> None:

    result = send_query_get(
        build_cars_endpoint(
            {
                "kategoriaPociagu": "TLK",
                "nrPociagu": 38170,
                "dataPrzyjazdu": "2026-06-05 06:23:00",
                "dataWyjazdu": "2026-06-05 02:20:00",
            },
            {"kodEPA": 5100136},
            {"kodEPA": 5100023},
        )
    )

    cars = find_bike_cars(result)
    print(json.dumps(cars, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
