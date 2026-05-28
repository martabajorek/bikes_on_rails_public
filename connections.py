import json
from datetime import date
from typing import Any

from api import send_query_post

CONNECTIONS_ENDPOINT = "https://api-gateway.intercity.pl/server/public/endpoint/Pociagi"


def build_connections_payload(
    selected_date: date,
    station_from: dict[str, Any],
    station_to: dict[str, Any],
) -> dict[str, Any]:
    date_text = selected_date.isoformat()
    station_from_code = station_from["kod"]
    station_to_code = station_to["kod"]

    return {
        "metoda": "wyszukajPolaczenia",
        "wersja": "1.5.6_desktop",
        "url": (
            "https://ebilet.intercity.pl/wyszukiwanie?"
            f"dwyj={date_text}"
            f"&swyj={station_from_code}"
            f"&sprzy={station_to_code}"
            "&time=01%3A50"
            "&przy=0"
            "&sprzez="
            "&ticket100=1010%3B1010"
            "&ticket50="
            "&polbez=1"
            "&ahan=FB"
        ),
        "dataWyjazdu": f"{date_text} 00:00:00",
        "stacjaWyjazdu": station_from_code,
        "stacjaPrzyjazdu": station_to_code,
        "stacjePrzez": [],
        "urzadzenieNr": 956,
    }

def parse_connections_result(result: dict[str, Any]) -> dict[str, Any]:
    connections = result["polaczenia"]
    direct_connections = [connection for connection in connections if len(connection["pociagi"]) == 1]
    bike_trains: list[dict[str, Any]] = []

    for connection in direct_connections:
        train = connection["pociagi"][0]
        if 24 not in train.get("typyMiejsc", []):
            continue

        bike_trains.append(
            {
                "nrPociagu": train.get("nrPociagu"),
                "kategoriaPociagu": train.get("kategoriaPociagu"),
                "nazwaPociagu": train.get("nazwaPociagu"),
                "dataWyjazdu": connection.get("dataWyjazdu", train.get("dataWyjazdu")),
                "dataPrzyjazdu": connection.get("dataPrzyjazdu", train.get("dataPrzyjazdu")),
                "czasJazdy": connection.get("czasJazdy", train.get("czasJazdy")),
            }
        )

    return {
        "number_of_connections": len(connections),
        "number_of_direct_connections": len(direct_connections),
        "number_of_direct_bike_trains": len(bike_trains),
        "bike_trains": bike_trains,
    }


# def main() -> None:
#     payload = build_connections_payload(date(2026, 6, 5), {"kod": 242}, {"kod": 41})
#     result = send_query_post(endpoint=CONNECTIONS_ENDPOINT, json=payload)
#     summary = parse_connections_result(result)
#     print(json.dumps(summary, ensure_ascii=False, indent=2))
#
#
# if __name__ == "__main__":
#     main()
