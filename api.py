import json
from typing import Any

import httpx


HEADERS = {
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


def send_query_get(endpoint) -> Any:

    with httpx.Client(http2=True, headers=HEADERS, timeout=30) as client:
        response = client.get(url=endpoint)
        response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            print('returning text')
            return response.text

def send_query_post(endpoint, json=None) -> Any:

    with httpx.Client(http2=True, headers=HEADERS, timeout=30) as client:
        response = client.post(url=endpoint, json=json)
        response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            print('returning text')
            return response.text

    # headers = {
    #     "User-Agent": (
    #         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #         "AppleWebKit/537.36 (KHTML, like Gecko) "
    #         "Chrome/125.0.0.0 Safari/537.36"
    #     ),
    #     "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    #     "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    #     "Referer": "https://www.intercity.pl/",
    #     "Origin": "https://www.intercity.pl",
    #     "Sec-Fetch-Dest": "image",
    #     "Sec-Fetch-Mode": "no-cors",
    #     "Sec-Fetch-Site": "same-site",
    # }

    # with httpx.Client(http2=True, headers=headers, timeout=20) as client:
    #     response = client.get(address)
    #     response.raise_for_status()

    # headers = {
    #     "User-Agent": (
    #         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #         "AppleWebKit/537.36 (KHTML, like Gecko) "
    #         "Chrome/125.0.0.0 Safari/537.36"
    #     ),
    #     "Accept": "application/json, text/plain, */*",
    #     "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    #     "Content-Type": "application/json",
    #     "Origin": "https://ebilet.intercity.pl",
    #     "Referer": "https://ebilet.intercity.pl/",
    # }

