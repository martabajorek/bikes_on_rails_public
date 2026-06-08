from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from api import send_query_get, send_query_post
from cars import build_cars_endpoint, find_bike_cars
from connections import (
    CONNECTIONS_ENDPOINT,
    build_connections_payload,
    parse_connections_result,
)
from seats import build_seats_endpoint, extract_bike_places


STATIONS_PATH = Path("stations_parsed.csv")


@st.cache_data
def load_stations() -> pd.DataFrame:
    return pd.read_csv(STATIONS_PATH)


def station_options(stations: pd.DataFrame) -> list[dict[str, object]]:
    return stations[["nazwa", "kod", "kodEPA"]].to_dict(orient="records")


def station_label(station: dict[str, object]) -> str:
    return str(station["nazwa"])


def build_seat_rows(
    parsed_connections: dict[str, object],
    station_from: dict[str, object],
    station_to: dict[str, object],
) -> list[dict[str, object]]:
    seat_rows: list[dict[str, object]] = []

    for connection in parsed_connections["bike_trains"]:
        cars_url = build_cars_endpoint(connection, station_from, station_to)
        cars_result = send_query_get(cars_url)
        bike_cars = find_bike_cars(cars_result)

        for car in bike_cars:
            seats_url = build_seats_endpoint(connection, car, station_from, station_to)
            svg_text = send_query_get(seats_url)
            bike_places = extract_bike_places(svg_text)

            for seat in bike_places:
                seat_rows.append(
                    {
                        "dataWyjazdu": connection["dataWyjazdu"],
                        "dataPrzyjazdu": connection["dataPrzyjazdu"],
                        "kategoriaPociagu": connection["kategoriaPociagu"],
                        "czasJazdy": connection["czasJazdy"],
                        "nrPociagu": connection["nrPociagu"],
                        "wagon": car["wagon"],
                        "wagonySchemat": car["wagonySchemat"],
                        "place_number": seat["place_number"],
                        "status": seat["status"],
                    }
                )

    return seat_rows


def main() -> None:
    st.set_page_config(page_title="Bikes On Rails", layout="centered")
    st.title("Bikes On Rails")

    stations = load_stations()
    options = station_options(stations)

    station_from = st.selectbox(
        "station_from",
        options,
        format_func=station_label,
        index=None,
        placeholder="Select station",
    )

    station_to = st.selectbox(
        "station_to",
        options,
        format_func=station_label,
        index=None,
        placeholder="Select station",
    )

    select_date = st.date_input(
        "select_date",
        value=date.today(),
        min_value=date.today(),
    )

    run_clicked = st.button("Run")

    if not (run_clicked and station_from and station_to):
        return

    connections_result = send_query_post(
        endpoint=CONNECTIONS_ENDPOINT,
        json=build_connections_payload(select_date, station_from, station_to),
    )
    parsed_connections = parse_connections_result(connections_result)
    seat_rows = build_seat_rows(parsed_connections, station_from, station_to)

    st.subheader("connections")
    st.json(parsed_connections)

    st.subheader("seats")
    if seat_rows:
        st.dataframe(pd.DataFrame(seat_rows), use_container_width=True)
    else:
        st.info("No bicycle seats found.")


if __name__ == "__main__":
    main()
