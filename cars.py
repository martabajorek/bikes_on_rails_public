import json
from typing import Any

from api import send_query_get

CARS_ENDPOINT = (
    "https://api-gateway.intercity.pl/grm/sklad/wbnet/TLK/38170/"
    "202606050623/5100136/202606050220/5100023"
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
    result = send_query_get(CARS_ENDPOINT)
    cars = find_bike_cars(result)
    print(json.dumps(cars, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
