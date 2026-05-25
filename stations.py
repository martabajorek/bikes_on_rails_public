import json
from pathlib import Path
from typing import Any

import httpx
import pandas as pd


STATIONS_ENDPOINT = (
    "https://api-gateway.intercity.pl/server/public/endpoint/Aktualizacja"
)
OUTPUT_JSON_PATH = Path("stations_parsed.json")
OUTPUT_CSV_PATH = Path("stations_parsed.csv")

EXCLUDED_STATION_KEYS = {
    "skrotKraju",
    "kraj",
    "szerokoscGeograficzna",
    "dlugoscGeograficzna",
}


def send_stations_query() -> Any:
    payload = {
        "metoda": "pobierzStacje",
        "ostatniaAktualizacjaData": "2026-05-24 08:13:48.048",
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


def clean_station_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned = {}

    for key, value in record.items():
        if key in EXCLUDED_STATION_KEYS:
            continue

        cleaned[key] = value

    return cleaned


def collect_stations(data: Any) -> list[dict[str, Any]]:
    stations: list[dict[str, Any]] = []

    if isinstance(data, list):
        for item in data:
            stations.extend(collect_stations(item))
        return stations

    if isinstance(data, dict):
        if data.get("skrotKraju") == "PL" and "nazwa" in data:
            stations.append(clean_station_record(data))

        for value in data.values():
            stations.extend(collect_stations(value))

    return stations


def save_as_json_text(stations: list[dict[str, Any]], path: Path) -> None:
    path.write_text(
        json.dumps(stations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_dataframe(stations: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(stations)


def save_as_csv(stations: list[dict[str, Any]], path: Path) -> None:
    if not stations:
        path.write_text("", encoding="utf-8")
        return

    build_dataframe(stations).to_csv(path, index=False)


def main() -> None:
    result = send_stations_query()

    if isinstance(result, str):
        print(result)
        return

    # print(json.dumps(result, ensure_ascii=False, indent=2))

    stations = collect_stations(result)
    save_as_json_text(stations, OUTPUT_JSON_PATH)
    save_as_csv(stations, OUTPUT_CSV_PATH)

    print(
        json.dumps(
            {
                "stations_found": len(stations),
                "json_file": str(OUTPUT_JSON_PATH),
                "csv_file": str(OUTPUT_CSV_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
