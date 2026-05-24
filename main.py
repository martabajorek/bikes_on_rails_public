import httpx


def main() -> None:
    address = "https://api-gateway.intercity.pl/grm/wagon/svg/wbnet/TLK/35170/14/2221,2033,WITHOUT_COMPARTMENTS/202606100501/202606100844/5100136/5100023"

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

        print(f"Status code: {response.status_code}")
        print(f"HTTP version: {response.http_version}")
        print(response.text)


if __name__ == "__main__":
    main()
