from __future__ import annotations

import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="APIx Airfare Intelligence", page_icon="✈", layout="wide")
st.markdown("<style>body{background:#07131f}.block-container{max-width:1280px;padding-top:2rem}h1{letter-spacing:-.04em}</style>", unsafe_allow_html=True)


def get(path: str, **params):
    try:
        response = requests.get(f"{API_URL}{path}", params=params, timeout=8)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        st.error(f"API unavailable: {error}")
        return []

st.title("Airfare Intelligence")
st.caption("SIH26056 · Real-time Airfare Price Index for India")

with st.sidebar:
    st.header("Search market")
    origin = st.selectbox("Origin", ["DEL", "BOM", "BLR", "MAA"])
    destination = st.selectbox("Destination", ["BOM", "BLR", "CCU", "HYD", "DEL"])
    passengers = st.number_input("Passengers", 1, 9, 1)
    st.caption("Demo data is seeded locally. Connect permitted sources through the adapter interface.")

index_rows = get("/api/v1/index/daily")
latest = index_rows[-1]["apix"] if index_rows else 100
routes = get("/api/v1/routes")
status = get("/api/v1/scraping/status")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Current APIx", f"{latest:.1f}", "Base = 100")
k2.metric("Observations", f"{status.get('observations', 0):,}")
k3.metric("Routes tracked", len(routes))
k4.metric("Sources", len(status.get("sources", [])))

left, right = st.columns([1.5, 1])
with left:
    st.subheader(f"APIx trend · {origin} → {destination}")
    trend = get("/api/v1/index/daily")
    if trend: st.line_chart(pd.DataFrame(trend).set_index("date")["apix"], height=300)
with right:
    st.subheader("Airline comparison")
    airlines = get("/api/v1/analytics/airlines", origin=origin, destination=destination)
    if airlines: st.bar_chart(pd.DataFrame(airlines).set_index("airline")["average_fare"], height=300)

st.subheader("Fare search")
results = get("/api/v1/fares", origin=origin, destination=destination, passengers=passengers)
if results:
    table = pd.DataFrame(results)[["airline", "flight_number", "total_fare", "availability", "source"]]
    table.columns = ["Airline", "Flight", "Total fare (INR)", "Seats", "Source"]
    st.dataframe(table, use_container_width=True, hide_index=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Booking window")
    lead = get("/api/v1/analytics/lead-time", origin=origin, destination=destination)
    if lead: st.line_chart(pd.DataFrame(lead).set_index("days")["average_fare"], height=240)
with c2:
    st.subheader("Tracked route basket")
    if routes: st.dataframe(pd.DataFrame(routes), use_container_width=True, hide_index=True)

st.caption("APIx is an MVP weighted equally across the seeded route basket; official MoSPI weights can be configured later.")


def main():
    pass
