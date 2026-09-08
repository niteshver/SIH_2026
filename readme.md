# Airfare Intelligence MVP

SIH26056 MVP: a seeded Indian airfare search, analytics, and APIx index service using Python, FastAPI, and Streamlit.

## Run locally with uv

```bash
uv sync
uv run uvicorn app:app --app-dir src --reload
uv run streamlit run src/dashboard.py
uv run pytest
```

Open `http://localhost:8501` for the dashboard and `http://localhost:8000/docs` for API docs.

## Deploy

Use Railway for the API and Streamlit services. The included `Dockerfile` starts FastAPI; the dashboard command is `streamlit run src/dashboard.py --server.address 0.0.0.0 --server.port 8501`. Vercel is suitable for a later frontend or API proxy, not for long-running Streamlit workers.

## Architecture

`src/app.py` contains the normalized fare model, deterministic 30-day `MockAirfareSource`, search endpoints, analytics, APIx, status, and the `PermittedCrawlerSource` extension point. Add Crawl4AI adapters only for sources that permit automated access; never bypass CAPTCHA, authentication, robots.txt, or access restrictions. Local Llama 3.1 can be integrated later through Ollama using `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.

The current APIx uses an equally weighted seeded route basket with a 100-point baseline. Replace this method and weights when the official methodology is available.
