import xml.etree.ElementTree as ET

from api import send_query_get


SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"
SEATS_ENDPOINT = "https://api-gateway.intercity.pl/grm/wagon/svg/wbnet/IC/1814/13/2124,2141,MIXED/202606061101/202606061440/5100136/5100023"


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
    svg_text = send_query_get(SEATS_ENDPOINT)

    bike_places = extract_bike_places(svg_text)

    if not bike_places:
        print("No bicycle places found.")
        return

    for place in bike_places:
        print(f"Miejsce {place['place_number']}: {place['status']}")


if __name__ == "__main__":
    main()
