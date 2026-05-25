import json
from typing import Any

import httpx


STATIONS_ENDPOINT = (
    "https://api-gateway.intercity.pl/server/public/endpoint/Aktualizacja"
)


def send_stations_query() -> Any:
    payload = {
        "metoda": "pobierzStacje",
        # "ostatniaAktualizacjaData": "2026-05-24 08:13:48.048",
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
        response = client.post(STATIONS_ENDPOINT, json=payload)
        response.raise_for_status()

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


def main() -> None:
    result = send_stations_query()

    if isinstance(result, str):
        print(result)
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
