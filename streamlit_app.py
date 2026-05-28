from datetime import date
from pathlib import Path
from html import escape

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


def build_seat_summaries(
    parsed_connections: dict[str, object],
    station_from: dict[str, object],
    station_to: dict[str, object],
    status_placeholder: st.delta_generator.DeltaGenerator,
) -> list[dict[str, object]]:
    seat_summaries: list[dict[str, object]] = []
    connections = parsed_connections["bike_trains"]
    total_connections = len(connections)

    for index, connection in enumerate(connections, start=1):
        status_placeholder.write(f"checking connection {index} of {total_connections}")
        cars_url = build_cars_endpoint(connection, station_from, station_to)
        cars_result = send_query_get(cars_url)
        bike_cars = find_bike_cars(cars_result)
        wagon_counts: dict[str, int] = {}

        for car in bike_cars:
            seats_url = build_seats_endpoint(connection, car, station_from, station_to)
            svg_text = send_query_get(seats_url)
            bike_places = extract_bike_places(svg_text)

            if bike_places:
                wagon_counts[car["wagon"]] = wagon_counts.get(car["wagon"], 0) + len(
                    bike_places
                )

        if wagon_counts:
            summary_text = "\n".join(
                f"{count} {'miejsce' if count == 1 else 'miejsca'} w wagonie {wagon}"
                for wagon, count in sorted(wagon_counts.items())
            )
        else:
            summary_text = "brak wolnych miejsc na rower"

        seat_summaries.append(
            {
                "nrPociagu": connection["nrPociagu"],
                "kategoriaPociagu": connection["kategoriaPociagu"],
                "nazwaPociagu": connection["nazwaPociagu"],
                "dataWyjazdu": connection["dataWyjazdu"],
                "dataPrzyjazdu": connection["dataPrzyjazdu"],
                "czasJazdy": connection["czasJazdy"],
                "summary": summary_text,
            }
        )

    return seat_summaries


def render_seat_table(df: pd.DataFrame) -> str:
    rows = []

    for _, row in df.iterrows():
        is_available = row["summary"] != "brak wolnych miejsc na rower"
        background = "background-color: #dff3df;" if is_available else ""
        summary_html = escape(str(row["summary"])).replace("\n", "<br>")

        rows.append(
            "<tr style='{background}'>"
            "<td>{nr}</td>"
            "<td>{kat}</td>"
            "<td>{name}</td>"
            "<td>{wyj}</td>"
            "<td>{przy}</td>"
            "<td>{czas}</td>"
            "<td>{summary}</td>"
            "</tr>".format(
                background=background,
                nr=escape(str(row["nrPociagu"])),
                kat=escape(str(row["kategoriaPociagu"])),
                name=escape(str(row["nazwaPociagu"])),
                wyj=escape(str(row["dataWyjazdu"])),
                przy=escape(str(row["dataPrzyjazdu"])),
                czas=escape(str(row["czasJazdy"])),
                summary=summary_html,
            )
        )

    return (
        "<table style='width:100%; border-collapse: collapse;'>"
        "<thead>"
        "<tr>"
        "<th style='text-align:left; border-bottom:1px solid #ddd; padding:6px;'>nrPociagu</th>"
        "<th style='text-align:left; border-bottom:1px solid #ddd; padding:6px;'>kategoriaPociagu</th>"
        "<th style='text-align:left; border-bottom:1px solid #ddd; padding:6px;'>nazwaPociagu</th>"
        "<th style='text-align:left; border-bottom:1px solid #ddd; padding:6px;'>dataWyjazdu</th>"
        "<th style='text-align:left; border-bottom:1px solid #ddd; padding:6px;'>dataPrzyjazdu</th>"
        "<th style='text-align:left; border-bottom:1px solid #ddd; padding:6px;'>czasJazdy</th>"
        "<th style='text-align:left; border-bottom:1px solid #ddd; padding:6px;'>summary</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def main() -> None:
    st.set_page_config(page_title="Bikes On Rails", layout="wide")
    st.title("Bikes On Rails")

    stations = load_stations()
    options = station_options(stations)

    _, controls_col, _ = st.columns([1, 2, 1])
    with controls_col:
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

    st.subheader("connections")
    st.write(f"number of connections: {parsed_connections['number_of_connections']}")
    st.write(
        f"number of bike trains: {parsed_connections['number_of_bike_trains']}"
    )
    st.dataframe(
        pd.DataFrame(parsed_connections["bike_trains"]),
        use_container_width=True,
    )

    st.subheader("seats")
    status_placeholder = st.empty()
    seat_summaries = build_seat_summaries(
        parsed_connections, station_from, station_to, status_placeholder
    )
    seat_df = pd.DataFrame(seat_summaries)
    st.markdown(render_seat_table(seat_df), unsafe_allow_html=True)
    status_placeholder.empty()


if __name__ == "__main__":
    main()
