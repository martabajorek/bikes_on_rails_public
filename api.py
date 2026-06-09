import json
from typing import Any

from curl_cffi import requests


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


class PkpApiError(RuntimeError):
    def __init__(self, status_code: int, status_message: str, body: str = "") -> None:
        super().__init__(f"{status_code} {status_message}")
        self.status_code = status_code
        self.status_message = status_message
        self.body = body


def _read_response(response: httpx.Response) -> Any:
    print(response.status_code)

    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise PkpApiError(
            response.status_code,
            response.reason_phrase,
            response.text,
        )

    try:
        return response.json()
    except json.JSONDecodeError:
        print("returning text")
        return response.text


def send_query_get(endpoint) -> Any:
    print(endpoint)
    response = requests.get(
        url=endpoint,
        headers=HEADERS,
        timeout=30,
        impersonate="chrome"
    )
    return _read_response(response)

def send_query_post(endpoint, json=None) -> Any:
    print(json)
    response = requests.post(
        url=endpoint,
        json=json,
        headers=HEADERS,
        timeout=30,
        impersonate="chrome"
    )
    return _read_response(response)

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

