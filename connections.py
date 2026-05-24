import json

import httpx


CONNECTIONS_ENDPOINT = "https://api-gateway.intercity.pl/server/public/endpoint/Pociagi"


def send_connections_query() -> dict:
    payload = {
        "metoda": "wyszukajPolaczenia",
        "wersja": "1.5.6_desktop",
        "url": "https://ebilet.intercity.pl/wyszukiwanie?dwyj=2026-06-05&swyj=242&sprzy=41&time=01%3A50&przy=0&sprzez=&ticket100=1010%3B1010&ticket50=&polbez=1&ahan=FB",
        "dataWyjazdu": "2026-06-05 00:00:00",
        "dataPrzyjazdu": "2026-06-05 23:59:59",
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


def main() -> None:
    result = send_connections_query()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
