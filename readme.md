# Real-Time Airfare Price Intelligence & Index Platform

> **Smart India Hackathon 2026 — SIH26056**

## 1. Problem Statement

### Development of a Real-time Airfare Price Index for India through Automated Web Scraping of Airline and Online Travel Aggregator Portals for Augmentation of the Consumer Price Index (CPI)

**Organization:** Ministry of Statistics and Programme Implementation (MoSPI)
**Department:** Data Informatics & Innovation Division (DIID)
**Category:** Software
**Theme:** Smart Automation
**Problem ID:** SIH26056

---

# 2. Problem Overview

Airfare in India is highly dynamic.

The price of the same flight route can change significantly depending on:

* Demand
* Day of the week
* Advance booking period
* Festival and holiday seasons
* Airline
* Fare class
* Taxes and fees
* Availability
* Market conditions

The current CPI framework relies primarily on manual collection of transportation prices. However, a large proportion of domestic air-ticket purchases now happen through airline websites and Online Travel Aggregators (OTAs).

This creates a major data-collection problem:

> **How can we automatically collect, standardize, analyze and monitor real-world airfare prices at high frequency across India?**

The SIH problem statement therefore proposes an automated system capable of collecting airfare information from airline portals and OTAs and using that data to construct a **Real-time Airfare Price Index (APIx)**.

---

# 3. Our Proposed Solution

We propose a **Real-Time Airfare Price Intelligence Platform** that works somewhat like a **search engine + web crawler + data warehouse + analytics engine** specifically for Indian flight prices.

Instead of manually visiting different airline and OTA websites, our platform will:

```text
User / Scheduler
       │
       ▼
Flight Search Request
       │
       ▼
Source Discovery
       │
       ├── Airline Websites
       ├── OTA Websites
       └── Other Permitted Sources
       │
       ▼
Web Scraping / Data Collection Engine
       │
       ▼
Raw Airfare Data
       │
       ▼
Data Cleaning & Normalization
       │
       ▼
Unified Airfare Database
       │
       ├───────────────┐
       ▼               ▼
Search Engine      Index Engine
       │               │
       ▼               ▼
Flight Prices     Airfare Price Index
       │               │
       └───────┬───────┘
               ▼
       Analytics Dashboard
               │
               ▼
          API / Reports
```

The important idea is that our system does **not** depend on a single website.

It creates a unified representation of airfare data from multiple permitted sources.

---

# 4. The Platform as an Airfare Search Engine

Our system can be thought of as a specialized search engine for airfare intelligence.

A conventional search engine performs:

```text
Websites
   ↓
Crawler
   ↓
Raw Pages
   ↓
Parser
   ↓
Search Index
   ↓
Search Results
```

Our platform performs:

```text
Airline / OTA Websites
          ↓
   Scraping Agents
          ↓
     Raw Quotes
          ↓
 Parser + Normalizer
          ↓
   Airfare Database
          ↓
   Search / Analytics
          ↓
 Price Intelligence
```

The difference is that our objective is not only to return a flight price.

We also preserve the **historical and statistical information** required to understand how airfare changes over time.

---

# 5. Why Existing Methods Are Not Enough

## Manual Data Collection

Manual collection has several limitations:

* Slow
* Expensive
* Difficult to scale
* Cannot continuously monitor prices
* Limited number of routes
* Limited historical information
* Difficult to reproduce

For dynamic airfare, a price collected once may become irrelevant shortly afterward.

---

## Single-Website Scraping

Scraping only one airline or OTA creates another problem.

For example:

```text
Source A → ₹4,500

Source B → ₹5,100

Source C → ₹4,200

Source D → ₹4,750
```

Looking at only one source does not provide a complete market picture.

Our system therefore uses a **multi-source architecture**.

---

# 6. Key Objectives

The platform will provide the following capabilities.

### 6.1 Automated Data Collection

Automatically collect airfare quotes from permitted airline and OTA sources.

Target sources mentioned in the SIH problem include:

* IndiGo
* Air India
* Air India Express
* Akasa Air
* SpiceJet
* Major Online Travel Aggregators

The official problem statement specifically identifies airline portals and leading OTAs as data sources.

---

### 6.2 Multi-Route Monitoring

Maintain a representative basket of Indian city pairs.

Example:

```text
DEL → BOM
DEL → BLR
BOM → BLR
DEL → CCU
BLR → HYD
MAA → DEL
```

The SIH problem specifically proposes representative city pairs selected using DGCA passenger-traffic data.

---

### 6.3 Advance-Purchase Windows

For each route, collect prices for different booking windows.

Example:

```text
T+1
T+7
T+15
T+30
T+45
```

This allows us to understand how airfare changes depending on how early a passenger books.

---

# 7. Core Architecture

```text
                    ┌───────────────────────┐
                    │    Route Scheduler    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Search Configuration │
                    │ Route + Date + Window │
                    └───────────┬───────────┘
                                │
                                ▼
              ┌─────────────────────────────────┐
              │       Scraping Orchestrator     │
              └───────────────┬─────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │ Airline Agent  │  │ OTA Agent      │  │ Future Sources │
 └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
                    ┌───────────────────┐
                    │ Raw Data Storage  │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ Data Cleaning     │
                    │ & Validation      │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ Normalization     │
                    └─────────┬─────────┘
                              ▼
              ┌─────────────────────────────┐
              │      Airfare Data Store     │
              └──────────────┬──────────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
          ┌──────────┐ ┌──────────┐ ┌──────────┐
          │ Search   │ │ Index    │ │ Analytics│
          │ Engine   │ │ Engine   │ │ Engine   │
          └────┬─────┘ └────┬─────┘ └────┬─────┘
               │             │             │
               └─────────────┼─────────────┘
                             ▼
                    ┌───────────────────┐
                    │ Interactive       │
                    │ Dashboard         │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ REST API / Export │
                    └───────────────────┘
```

---

# 8. Web Scraping Engine

The scraping engine is the foundation of the platform.

Possible technologies:

* Python
* Playwright
* Selenium
* Scrapy
* Requests where permitted
* BeautifulSoup for static HTML

The SIH specification explicitly mentions Python with tools such as Scrapy, Selenium and Playwright.

---

# 9. Search Query Model

Every scraping request can be represented as a standardized search query.

```json
{
  "origin": "DEL",
  "destination": "BOM",
  "departure_date": "2026-10-15",
  "advance_window": 30,
  "passengers": 1,
  "cabin_class": "economy"
}
```

The scraper converts this generic query into the format required by each source.

---

# 10. Raw Airfare Data

Every collected quote should preserve the original observation.

Example:

```json
{
  "source": "airline_source",
  "origin": "DEL",
  "destination": "BOM",
  "flight_date": "2026-10-15",
  "scraped_at": "2026-09-15T10:30:00",
  "airline": "Example Airline",
  "flight_number": "XX123",
  "fare_class": "Economy",
  "base_fare": 3500,
  "taxes": 850,
  "fees": 150,
  "total_fare": 4500,
  "currency": "INR",
  "availability": "available"
}
```

The SIH requirement explicitly calls for metadata such as origin, destination, carrier, advance-purchase window, fare class, base fare, taxes and total fare.

---


# 16. Example Index Calculation

Suppose the system tracks three representative routes:

| Route   | Weight | Base Price | Current Price |
| ------- | -----: | ---------: | ------------: |
| DEL-BOM |    40% |     ₹4,000 |        ₹4,400 |
| DEL-BLR |    35% |     ₹4,500 |        ₹4,950 |
| BOM-BLR |    25% |     ₹3,000 |        ₹3,150 |

The system calculates the weighted movement of the representative basket.

The exact production methodology should follow the methodology and weights prescribed by the concerned authority rather than using arbitrary weights.

---

# 17. Dashboard

The platform will provide an interactive dashboard.

## Main Dashboard

```text
┌──────────────────────────────────────────────────────┐
│          REAL-TIME AIRFARE PRICE INDEX               │
├──────────────────────────────────────────────────────┤
│                                                      │
│       APIx: 127.4       ▲ 3.2%                      │
│                                                      │
├───────────────────────┬──────────────────────────────┤
│ Daily Trend           │ Route Heatmap                │
│                       │                              │
│     ╱╲                │ DEL-BOM  █████              │
│  ╱╲╱  ╲               │ DEL-BLR  ████               │
│ ╱      ╲              │ BOM-BLR  ███                │
│                       │                              │
├───────────────────────┴──────────────────────────────┤
│ Advance Booking Elasticity                           │
│                                                      │
│ T+1 → T+7 → T+15 → T+30 → T+45                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---


# 20. Technology Stack

## Backend

```text
Python
FastAPI
Pydantic
```

## Scraping

```text
Playwright
CRAWL4AI
```

## Database

```text
PostgreSQL
Redis
```

## Data Processing

```text
Scipy
Algo
```

## Dashboard

```text
React / Next.js
Plotly
ECharts
```

## Infrastructure

```text
Docker
GitHub Actions
```
---

# 23. Ethical and Compliant Scraping

The system must **not** be designed to bypass security controls illegally.

The scraping architecture should respect:

* `robots.txt`
