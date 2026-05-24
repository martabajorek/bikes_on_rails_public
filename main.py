import httpx
import xml.etree.ElementTree as ET


SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


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
    address = "https://api-gateway.intercity.pl/grm/wagon/svg/wbnet/IC/1814/13/2124,2141,MIXED/202606061101/202606061440/5100136/5100023"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.intercity.pl/",
        "Origin": "https://www.intercity.pl",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
    }

    with httpx.Client(http2=True, headers=headers, timeout=20) as client:
        response = client.get(address)
        response.raise_for_status()

    bike_places = extract_bike_places(response.text)

    if not bike_places:
        print("No bicycle places found.")
        return

    for place in bike_places:
        print(f"Miejsce {place['place_number']}: {place['status']}")


if __name__ == "__main__":
    main()
