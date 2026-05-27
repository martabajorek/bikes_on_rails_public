import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

from api import send_query_get


SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


def compact_datetime(value: str) -> str:
    return datetime.fromisoformat(value).strftime("%Y%m%d%H%M")


def build_seats_endpoint(
    connection: dict[str, Any],
    car: dict[str, Any],
    station_from: dict[str, Any],
    station_to: dict[str, Any],
) -> str:
    return (
        "https://api-gateway.intercity.pl/grm/wagon/svg/wbnet/"
        f"{connection['kategoriaPociagu']}/{connection['nrPociagu']}/"
        f"{car['wagon']}/{car['wagonySchemat']}/"
        f"{compact_datetime(connection['dataWyjazdu'])}/"
        f"{compact_datetime(connection['dataPrzyjazdu'])}/"
        f"{station_from['kodEPA']}/"
        f"{station_to['kodEPA']}"
    )


def extract_bike_places(svg_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(svg_text)
    bike_places = []

    for group in root.iter(f"{SVG_NAMESPACE}g"):
        label = group.get("aria-label", "")

        if "Miejsce dla osoby z rowerem" not in label:
            continue

        label_parts = [part.strip() for part in label.split(",") if part.strip()]
        place_number = label_parts[0].replace("Miejsce ", "").replace(" klasa 2", "")
        status = label_parts[2]

        bike_places.append(
            {
                "place_number": place_number,
                "status": status,
            }
        )

    return bike_places


def main() -> None:
    svg_text = send_query_get(
        build_seats_endpoint(
            {
                "kategoriaPociagu": "IC",
                "nrPociagu": 1814,
                "dataWyjazdu": "2026-06-06 11:01:00",
                "dataPrzyjazdu": "2026-06-06 14:40:00",
            },
            {"wagon": 13, "wagonySchemat": "MIXED"},
            {"kodEPA": 5100136},
            {"kodEPA": 5100023},
        )
    )

    bike_places = extract_bike_places(svg_text)

    if not bike_places:
        print("No bicycle places found.")
        return

    for place in bike_places:
        print(f"Miejsce {place['place_number']}: {place['status']}")


if __name__ == "__main__":
    main()
