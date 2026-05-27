from datetime import date
from pathlib import Path
import random
import time

import pandas as pd
import streamlit as st

from api import send_query_get, send_query_post
from cars import build_cars_endpoint, find_bike_cars
from connections import build_connections_payload, parse_connections_result
from seats import build_seats_endpoint, extract_bike_places


STATIONS_PATH = Path("stations_parsed.csv")


@st.cache_data
def load_stations() -> pd.DataFrame:
    return pd.read_csv(STATIONS_PATH)


def station_options(stations: pd.DataFrame) -> list[dict[str, object]]:
    return stations[["nazwa", "kod", "kodEPA"]].to_dict(orient="records")


def station_label(station: dict[str, object]) -> str:
    return str(station["nazwa"])


def sleep_between_queries() -> None:
    time.sleep(random.uniform(3.5, 6.5))


def build_seat_row(
    connection: dict[str, object],
    car: dict[str, object],
    seat: dict[str, str],
) -> dict[str, object]:
    return {
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

    st.divider()
    st.write(
        {
            "station_from": station_from,
            "station_to": station_to,
            "select_date": select_date.isoformat(),
        }
    )

    if run_clicked and station_from and station_to:
        with st.spinner("Querying connections, cars, and seats..."):
            connections_result = send_query_post(
                endpoint="https://api-gateway.intercity.pl/server/public/endpoint/Pociagi",
                json=build_connections_payload(select_date, station_from, station_to),
            )
            parsed_connections = parse_connections_result(connections_result)
            seat_rows: list[dict[str, object]] = []

            for connection in parsed_connections["bike_trains"]:
                sleep_between_queries()
                cars_result = send_query_get(
                    build_cars_endpoint(connection, station_from, station_to)
                )
                bike_cars = find_bike_cars(cars_result)

                for car in bike_cars:
                    sleep_between_queries()
                    svg_text = send_query_get(
                        build_seats_endpoint(connection, car, station_from, station_to)
                    )
                    bike_places = extract_bike_places(svg_text)

                    for seat in bike_places:
                        seat_rows.append(build_seat_row(connection, car, seat))

        st.subheader("seats")
        st.write(
            {
                "number_of_connections": parsed_connections["number_of_connections"],
                "number_of_bike_trains": parsed_connections["number_of_bike_trains"],
                "number_of_seats": len(seat_rows),
            }
        )

        if seat_rows:
            st.dataframe(pd.DataFrame(seat_rows), use_container_width=True)
        else:
            st.info("No bicycle seats found.")


if __name__ == "__main__":
    main()
