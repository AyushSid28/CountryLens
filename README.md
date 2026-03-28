# CountryLens

AI agent that answers questions about countries using real-time data from the REST Countries API. Built with LangGraph, FastAPI, and Groq.

Live Demo: https://countrylens.onrender.com
Video Walkthrough: https://www.loom.com/share/beead33d358742c88fe2fc9d24c02e6f

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

- Conditional edge in LangGraph skips API call on invalid input
- In-memory TTL cache (5 min) avoids repeated API calls for same country
- Exponential backoff retry on API failures (1s, 2s, 4s...)
- Best-match logic to pick correct country when API returns multiple results
- Strict synthesis prompt to prevent hallucination

## Limitations

- One country per query
- LLM adds ~1-2s latency per request
- Cache resets on server restart
- Accuracy depends on REST Countries API

## What I'd add for production

- Redis for distributed cache
- Rate limiting on /query
- OpenTelemetry tracing across nodes
- Prompt injection guards
