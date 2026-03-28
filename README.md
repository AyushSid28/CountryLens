# CountryLens

AI agent that answers questions about countries using real-time data from the REST Countries API. Built with LangGraph, FastAPI, and Groq.

Live Demo: https://countrylens.onrender.com
Video Walkthrough: https://www.loom.com/share/e567a98fa4874b5d9aa1dafb7f1d6e8b

## How it works

Three-step LangGraph pipeline:

1. Intent Parser — LLM extracts country name and user intent from the question
2. API Tool — fetches data from REST Countries API with caching and retry
3. Synthesizer — LLM writes a clean answer using only the fetched data

If the parser can't find a country, it skips the API call and returns an error message directly.

## Setup

```bash
git clone https://github.com/AyushSid28/CountryLens.git
cd CountryLens
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000 for the UI or http://localhost:8000/docs for Swagger.

## Docker

```bash
docker build -t countrylens .
docker run -p 8000:8000 --env-file .env countrylens
```

## API

POST /query
```json
{ "question": "What is the capital of France?" }
```

GET /health — returns status and version

## Tech used

- LangGraph for agent orchestration
- Groq (Llama 3.3 70B) for LLM
- FastAPI + Uvicorn
- httpx for async API calls
- cachetools for TTL caching
- Pydantic for validation
- Docker for containerization

## Design choices

If the intent parser can't find a valid country, the flow skips the API call entirely and goes straight to the synthesizer with an error. No wasted API calls.

The API responses are cached in-memory for 5 minutes so if someone asks about the same country twice, the second response is instant.

If the REST Countries API fails, the agent retries with exponential backoff (1s, 2s, 4s) instead of crashing. Gives the API time to recover.

## Limitations

It only handles one country per query right now. Asking "compare India and China" will only pick up one.

Every request makes two LLM calls (parsing + synthesis) which adds about 1-2 seconds of latency.

The cache is in-memory so it resets every time the server restarts. No persistence across deployments.

## What I'd add for production

Right now the cache is in-memory so it resets on restart and doesn't work across multiple instances. I'd swap it with Redis.

The /query endpoint has no rate limiting so anyone can spam it and burn through API credits. Adding a rate limiter would fix that.

For debugging latency issues I'd add OpenTelemetry tracing across the LangGraph nodes so I can see exactly which step is slow.


