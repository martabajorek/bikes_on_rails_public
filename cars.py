import json
from typing import Any

import httpx


CARS_ENDPOINT = (
    "https://api-gateway.intercity.pl/grm/sklad/wbnet/TLK/38170/"
    "202606050623/5100136/202606050220/5100023"
)


def send_cars_query() -> Any:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.intercity.pl",
        "Referer": "https://www.intercity.pl/",
    }

    with httpx.Client(http2=True, headers=headers, timeout=30) as client:
        response = client.get(CARS_ENDPOINT)
        response.raise_for_status()

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


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
    result = send_cars_query()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
