# Airfare Intelligence MVP

Hackathon MVP: route-aware sitemap generation, permitted Crawl4AI extraction hooks, SHA-256 deduplication, Ollama/Llama 3.1 readiness, FastAPI, and a React + Plotly dashboard.

## Local

```bash
uv sync
uv run uvicorn app:app --app-dir src --reload
cd web && npm install && npm run dev
```

Open `http://localhost:5173`. Set `VITE_API_URL=http://localhost:8000` if the API is not local. Optional crawler/model setup: `uv sync --extra crawler --extra local-llm`, install Crawl4AI browser dependencies, install Ollama, then `ollama pull llama3.1:latest`.

## Railway deployment

1. Create a Railway project from this repository.
2. Create an **API service** with root `/`, Dockerfile `Dockerfile`, and variables `PERMITTED_DOMAINS`, `CORS_ORIGINS`, `OLLAMA_BASE_URL`, and `OLLAMA_MODEL=llama3.1:latest`. Railway provides `PORT`; do not hardcode it. Healthcheck: `/health`.
3. Deploy. The API start command is already in the Dockerfile. Copy its public URL.
4. Create a second service for the React app, root directory `web`, Dockerfile `web/Dockerfile`, and `VITE_API_URL=<API public URL>`. Expose port `4173` and use `/` as the healthcheck.
5. Redeploy the web service after changing `VITE_API_URL` because Vite embeds it at build time.

Before deployment: replace demo data with a database/object store for persistence, set an explicit permitted-domain allowlist, set `CORS_ORIGINS` to the web URL instead of `*`, install Crawl4AI browser dependencies in the API image, and add rate limits/timeouts. A laptop Ollama process is not reachable from Railway; deploy Ollama on a reachable GPU/VM service and set its HTTPS URL, or leave it unavailable and use the visible fallback warning. Never crawl login pages, CAPTCHAs, disallowed robots, or restricted domains.

## API flow

`POST /api/v1/sitemap` accepts `domain`, `origin`, and `destination`, then returns route query URLs. `POST /api/v1/scrape` queues those URLs and returns normalized records; replace the marked adapter with `AsyncWebCrawler`, `CrawlerRunConfig`, `DefaultMarkdownGenerator`, and JSON extraction on permitted domains. Store `content_hash=sha256(canonical_url + cleaned_content)` to prevent duplicate fare records. The UI exposes booking URLs, route history, airline comparison, and crawl/model status.

Streamlit remains available as a fallback: `uv run streamlit run src/dashboard.py`.
