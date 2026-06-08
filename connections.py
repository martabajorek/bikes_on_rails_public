import json
from typing import Any

from api import send_query_post

CONNECTIONS_ENDPOINT = "https://api-gateway.intercity.pl/server/public/endpoint/Pociagi"

CONNECTIONS_PAYLOAD = {
    "metoda": "wyszukajPolaczenia",
    "wersja": "1.5.6_desktop",
    "url": "https://ebilet.intercity.pl/wyszukiwanie?dwyj=2026-06-05&swyj=242&sprzy=41&time=01%3A50&przy=0&sprzez=&ticket100=1010%3B1010&ticket50=&polbez=1&ahan=FB",
    "dataWyjazdu": "2026-06-05 00:00:00",
    "stacjaWyjazdu": 242,
    "stacjaPrzyjazdu": 41,
    "stacjePrzez": [],
    "urzadzenieNr": 956,
}

def parse_connections_result(result: dict[str, Any]) -> dict[str, Any]:
    connections = result["polaczenia"]
    bike_trains: list[dict[str, Any]] = []

    for connection in connections:
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
        "number_of_bike_trains": len(bike_trains),
        "bike_trains": bike_trains,
    }


def main() -> None:
    result = send_query_post(endpoint=CONNECTIONS_ENDPOINT, json=CONNECTIONS_PAYLOAD)
    summary = parse_connections_result(result)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
