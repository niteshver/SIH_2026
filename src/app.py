from __future__ import annotations

import os
import random
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from statistics import mean
from typing import Protocol

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class Fare(BaseModel):
    origin: str
    destination: str
    flight_date: date
    scraped_at: datetime
    airline: str
    flight_number: str
    fare_class: str = "Economy"
    advance_purchase_days: int
    base_fare: float
    taxes: float
    fees: float
    total_fare: float
    currency: str = "INR"
    availability: int
    source: str


class FareSource(Protocol):
    name: str
    def collect(self, days: int = 30) -> list[Fare]: ...


class MockAirfareSource:
    name = "mock-market"
    routes = [("DEL", "BOM"), ("DEL", "BLR"), ("BOM", "BLR"), ("DEL", "CCU"), ("BLR", "HYD"), ("MAA", "DEL")]
    airlines = [("IndiGo", "6E"), ("Air India", "AI"), ("Akasa Air", "QP")]

    def collect(self, days: int = 30) -> list[Fare]:
        rng = random.Random(26056)
        now = datetime.now(UTC)
        rows: list[Fare] = []
        for day_offset in range(days):
            scraped = now - timedelta(days=days - day_offset - 1)
            for route_index, (origin, destination) in enumerate(self.routes):
                for airline_index, (airline, code) in enumerate(self.airlines):
                    for lead in (1, 7, 15, 30, 45):
                        base = 2800 + route_index * 260 + airline_index * 180 + lead * -12
                        seasonal = 300 * ((day_offset + route_index) % 7 == 4)
                        jitter = rng.randint(-130, 180)
                        fare = max(1800, base + seasonal + jitter)
                        taxes = round(fare * 0.18, 2)
                        fees = 249.0
                        rows.append(Fare(origin=origin, destination=destination,
                            flight_date=(scraped + timedelta(days=lead)).date(), scraped_at=scraped,
                            airline=airline, flight_number=f"{code}{120 + route_index * 7 + airline_index}",
                            advance_purchase_days=lead, base_fare=round(fare, 2), taxes=taxes,
                            fees=fees, total_fare=round(fare + taxes + fees, 2),
                            availability=rng.randint(2, 9), source=self.name))
        return rows


class PermittedCrawlerSource:
    """Extension point for Crawl4AI adapters. Only crawl sources with permission."""
    name = "permitted-crawl4ai"
    def collect(self, days: int = 30) -> list[Fare]:
        return []


DATA = MockAirfareSource().collect(30)
app = FastAPI(title="Airfare Intelligence API", version="0.1.0")


def filtered(origin: str | None = None, destination: str | None = None, flight_date: date | None = None,
             airline: str | None = None) -> list[Fare]:
    return [row for row in DATA if (not origin or row.origin == origin.upper())
            and (not destination or row.destination == destination.upper())
            and (not flight_date or row.flight_date == flight_date)
            and (not airline or row.airline == airline)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "airfare-api"}


@app.get("/api/v1/fares", response_model=list[Fare])
def fares(origin: str = Query("DEL"), destination: str = Query("BOM"), flight_date: date | None = None,
          passengers: int = Query(1, ge=1, le=9), cabin: str = "Economy") -> list[Fare]:
    del passengers, cabin
    return filtered(origin, destination, flight_date)


@app.get("/api/v1/fares/history")
def history(origin: str = "DEL", destination: str = "BOM") -> list[dict]:
    rows = filtered(origin, destination)
    grouped: dict[date, list[float]] = defaultdict(list)
    for row in rows: grouped[row.scraped_at.date()].append(row.total_fare)
    return [{"date": key.isoformat(), "average_fare": round(mean(values), 2), "min_fare": min(values), "max_fare": max(values)} for key, values in sorted(grouped.items())]


@app.get("/api/v1/routes")
def routes() -> list[dict]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in DATA: grouped[f"{row.origin}-{row.destination}"].append(row.total_fare)
    return [{"route": route, "average_fare": round(mean(values), 2), "observations": len(values)} for route, values in sorted(grouped.items())]


@app.get("/api/v1/index/daily")
def daily_index() -> list[dict]:
    history_rows = history()
    baseline = mean(item["average_fare"] for item in history_rows)
    return [{"date": item["date"], "apix": round(item["average_fare"] / baseline * 100, 2)} for item in history_rows]


@app.get("/api/v1/index/weekly")
def weekly_index() -> list[dict]:
    rows = daily_index()
    return [{"period": f"Week {index // 7 + 1}", "apix": round(mean(x["apix"] for x in rows[index:index + 7]), 2)} for index in range(0, len(rows), 7)]


@app.get("/api/v1/index/monthly")
def monthly_index() -> list[dict]:
    rows = daily_index()
    return [{"period": "Current month", "apix": round(mean(x["apix"] for x in rows), 2)}]


@app.get("/api/v1/analytics/airlines")
def airline_analytics(origin: str = "DEL", destination: str = "BOM") -> list[dict]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in filtered(origin, destination): grouped[row.airline].append(row.total_fare)
    return [{"airline": key, "average_fare": round(mean(values), 2), "min_fare": round(min(values), 2)} for key, values in sorted(grouped.items())]


@app.get("/api/v1/analytics/lead-time")
def lead_time(origin: str = "DEL", destination: str = "BOM") -> list[dict]:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in filtered(origin, destination): grouped[row.advance_purchase_days].append(row.total_fare)
    return [{"days": key, "average_fare": round(mean(values), 2)} for key, values in sorted(grouped.items())]


@app.get("/api/v1/scraping/status")
def scraping_status() -> dict:
    return {"last_run": max(row.scraped_at for row in DATA).isoformat(), "sources": ["mock-market", "permitted-crawl4ai"], "observations": len(DATA), "mode": "demo"}


def main() -> None:
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
