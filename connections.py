import json
from typing import Any

import httpx


CONNECTIONS_ENDPOINT = "https://api-gateway.intercity.pl/server/public/endpoint/Pociagi"


def send_connections_query() -> dict:
    payload = {
        "metoda": "wyszukajPolaczenia",
        "wersja": "1.5.6_desktop",
        "url": "https://ebilet.intercity.pl/wyszukiwanie?dwyj=2026-06-05&swyj=242&sprzy=41&time=01%3A50&przy=0&sprzez=&ticket100=1010%3B1010&ticket50=&polbez=1&ahan=FB",
        "dataWyjazdu": "2026-06-05 00:00:00",
        # "dataPrzyjazdu": "2026-06-05 23:59:59",
        "stacjaWyjazdu": 242,
        "stacjaPrzyjazdu": 41,
        "stacjePrzez": [],
        "polaczeniaBezposrednie": 0,
        "polaczeniaNajszybsze": 0,
        "liczbaPolaczen": 0,
        "czasNaPrzesiadkeMin": 5,
        "czasNaPrzesiadkeMax": 1440,
        "liczbaPrzesiadekMax": 2,
        "kategoriePociagow": [],
        "kodyPrzewoznikow": [],
        "rodzajeMiejsc": [],
        "typyMiejsc": [],
        "braille": 0,
        "atrybutyHandlowe": [],
        "urzadzenieNr": 956,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://ebilet.intercity.pl",
        "Referer": "https://ebilet.intercity.pl/",
    }

    with httpx.Client(http2=True, headers=headers, timeout=30) as client:
        response = client.post(CONNECTIONS_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()


def contains_value(value: Any, expected: Any) -> bool:
    if value == expected:
        return True

    if isinstance(value, str) and value == str(expected):
        return True

    if isinstance(value, list):
        return any(contains_value(item, expected) for item in value)

    if isinstance(value, dict):
        return any(contains_value(item, expected) for item in value.values())

    return False


def get_first(train: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in train:
            return train[key]

    return None


def collect_trains(data: Any) -> list[dict[str, Any]]:
    trains = []

    if isinstance(data, list):
        for item in data:
            trains.extend(collect_trains(item))

    if isinstance(data, dict):
        train_number = get_first(data, ["nrPociagu", "nrPociągu", "numerPociagu"])
        if train_number is not None:
            trains.append(data)

        for value in data.values():
            trains.extend(collect_trains(value))

    return trains


def parse_connections_result(result: dict[str, Any]) -> dict[str, Any]:
    trains = collect_trains(result)
    trains_with_bike_places = [
        train for train in trains if contains_value(train.get("typyMiejsc"), 24)
    ]

    return {
        "number_of_trains": len(trains),
        "number_of_trains_with_bike_places": len(trains_with_bike_places),
        "trains_with_bike_places": [
            {
                "nrPociągu": get_first(
                    train, ["nrPociagu", "nrPociągu", "numerPociagu"]
                ),
                "kategoriaPociągu": get_first(
                    train,
                    ["kategoriaPociagu", "kategoriaPociągu", "kategoriaPociÄ…gu"],
                ),
                "dataWyjazdu": train.get("dataWyjazdu"),
                "dataPrzyjazdu": train.get("dataPrzyjazdu"),
                "czasJazdy": train.get("czasJazdy"),
            }
            for train in trains_with_bike_places
        ],
    }


def main() -> None:
    result = send_connections_query()
    summary = parse_connections_result(result)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
