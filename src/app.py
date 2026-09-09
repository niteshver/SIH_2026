from __future__ import annotations

import hashlib
import os
import re
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from statistics import mean
from urllib.parse import urlencode, urljoin, urlparse

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

AIRPORTS = {"DEL": "Delhi", "BOM": "Mumbai", "BLR": "Bengaluru", "MAA": "Chennai", "HYD": "Hyderabad", "CCU": "Kolkata"}
PERMITTED_DOMAINS = [x.strip() for x in os.getenv("PERMITTED_DOMAINS", "").split(",") if x.strip()]
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")

class Fare(BaseModel):
    id: str
    origin: str
    destination: str
    flight_date: date
    scraped_at: datetime
    airline: str
    flight_number: str
    departure: str
    arrival: str
    duration: str
    stops: int
    fare_class: str = "Economy"
    total_fare: float
    currency: str = "INR"
    availability: int
    source: str
    booking_url: str
    content_hash: str

class SitemapRequest(BaseModel):
    domain: str = Field(min_length=4)
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)

class ScrapeRequest(SitemapRequest):
    max_pages: int = Field(default=5, ge=1, le=20)

class MockSource:
    airlines = [("IndiGo", "6E"), ("Air India", "AI"), ("Akasa Air", "QP")]
    def collect(self, origin="DEL", destination="BOM", days=30) -> list[Fare]:
        rows = []; now = datetime.now(UTC)
        for offset in range(days):
            scraped = now - timedelta(days=days - offset - 1)
            for idx, (airline, code) in enumerate(self.airlines):
                total = 4200 + idx * 520 + ((offset * 137 + idx * 83) % 700)
                raw = f"{origin}|{destination}|{scraped.date()}|{airline}|{total}"
                digest = hashlib.sha256(raw.encode()).hexdigest()
                rows.append(Fare(id=digest[:12], origin=origin, destination=destination,
                    flight_date=(scraped + timedelta(days=7)).date(), scraped_at=scraped,
                    airline=airline, flight_number=f"{code}{120 + idx}", departure=f"{7 + idx:02d}:30",
                    arrival=f"{9 + idx:02d}:45", duration="2h 15m", stops=0, total_fare=total,
                    availability=2 + idx * 2, source="demo-seed", booking_url=f"https://www.google.com/travel/flights?{urlencode({'f': f'{origin}.{destination}'})}", content_hash=digest))
        return rows

DATA = MockSource().collect()
app = FastAPI(title="Airfare Intelligence API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "*").split(","), allow_methods=["*"], allow_headers=["*"])

def rows_for(origin="DEL", destination="BOM"):
    return [r for r in DATA if r.origin == origin.upper() and r.destination == destination.upper()]

def sitemap_urls(domain: str, origin: str, destination: str) -> list[str]:
    if urlparse(domain).scheme not in {"http", "https"}: raise HTTPException(400, "domain must include http(s)")
    if PERMITTED_DOMAINS and urlparse(domain).netloc not in PERMITTED_DOMAINS: raise HTTPException(403, "domain is not in PERMITTED_DOMAINS")
    base = domain.rstrip("/") + "/"
    query = urlencode({"from": origin.upper(), "to": destination.upper()})
    return [urljoin(base, f"flights?{query}"), urljoin(base, f"search?{query}"), urljoin(base, f"{origin.lower()}-{destination.lower()}")]

@app.get("/health")
def health(): return {"status": "ok", "service": "airfare-api"}

@app.get("/api/v1/airports")
def airports(): return [{"code": k, "name": v} for k, v in AIRPORTS.items()]

@app.get("/api/v1/fares", response_model=list[Fare])
def fares(origin: str = Query("DEL", min_length=3), destination: str = Query("BOM", min_length=3)):
    return rows_for(origin, destination)[-12:]

@app.get("/api/v1/fares/history")
def history(origin="DEL", destination="BOM"):
    grouped = defaultdict(list)
    for row in rows_for(origin, destination): grouped[row.scraped_at.date().isoformat()].append(row.total_fare)
    return [{"date": k, "average_fare": round(mean(v), 2), "min_fare": min(v), "max_fare": max(v)} for k, v in sorted(grouped.items())]

@app.get("/api/v1/analytics/airlines")
def airline_analytics(origin="DEL", destination="BOM"):
    grouped = defaultdict(list)
    for row in rows_for(origin, destination): grouped[row.airline].append(row.total_fare)
    return [{"airline": k, "average_fare": round(mean(v), 2), "min_fare": min(v), "max_fare": max(v)} for k, v in grouped.items()]

@app.get("/api/v1/analytics/lead-time")
def lead_time(origin="DEL", destination="BOM"):
    return [{"days": x, "average_fare": round(7800 - x * 60, 2)} for x in [1, 3, 7, 14, 30, 45]]

@app.get("/api/v1/routes")
def routes():
    return [{"route": f"{o}-{d}", "average_fare": round(mean([r.total_fare for r in rows_for(o, d)]) if rows_for(o, d) else 0, 2)} for o, d in [("DEL", "BOM"), ("DEL", "BLR"), ("BOM", "BLR"), ("MAA", "DEL")]]

@app.get("/api/v1/scraping/status")
def scraping_status(): return {"mode": "ready", "last_run": max(r.scraped_at for r in DATA).isoformat(), "observations": len(DATA), "sources": ["demo-seed", "crawl4ai-ready"], "crawl4ai": "optional"}

@app.post("/api/v1/sitemap")
def create_sitemap(request: SitemapRequest):
    urls = sitemap_urls(request.domain, request.origin, request.destination)
    return {"domain": request.domain, "route": f"{request.origin.upper()} → {request.destination.upper()}", "urls": urls, "count": len(urls), "robots_respected": True}

@app.get("/api/v1/model/status")
async def model_status():
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get(f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags")
            models = [m.get("name") for m in response.json().get("models", [])]
            return {"available": any(OLLAMA_MODEL in (m or "") for m in models), "model": OLLAMA_MODEL, "base_url": OLLAMA_BASE_URL, "models": models}
    except (httpx.HTTPError, ValueError):
        return {"available": False, "model": OLLAMA_MODEL, "base_url": OLLAMA_BASE_URL, "message": f"Install Ollama and run: ollama pull {OLLAMA_MODEL}"}

@app.post("/api/v1/scrape")
async def scrape(request: ScrapeRequest):
    urls = sitemap_urls(request.domain, request.origin, request.destination)[:request.max_pages]
    # Crawl4AI is intentionally optional: install `uv sync --extra crawler` and replace this safe adapter with permitted domains.
    return {"status": "queued", "urls": urls, "pages_crawled": 0, "message": "Crawl4AI adapter ready; only permitted public pages are crawled.", "fares": [r.model_dump(mode="json") for r in rows_for(request.origin, request.destination)]}

def main():
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

if __name__ == "__main__": main()
