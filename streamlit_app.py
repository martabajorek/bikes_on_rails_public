from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st


STATIONS_PATH = Path("stations_parsed.csv")


@st.cache_data
def load_stations() -> pd.DataFrame:
    return pd.read_csv(STATIONS_PATH)


def station_options(stations: pd.DataFrame) -> list[dict[str, object]]:
    return stations[["nazwa", "kod", "kodEPA"]].to_dict(orient="records")


def station_label(station: dict[str, object]) -> str:
    return str(station["nazwa"])


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

    st.divider()
    st.write(
        {
            "station_from": station_from,
            "station_to": station_to,
            "select_date": select_date.isoformat(),
        }
    )


if __name__ == "__main__":
    main()
