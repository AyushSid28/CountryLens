import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.graph import build_graph
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    QueryMetadata,
    HealthResponse,
    ErrorResponse,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graph
    logger.info("Building LangGraph agent...")
    _graph = build_graph()
    logger.info("Agent ready")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Country Agent API",
    description="AI-powered country information agent built with LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/query",
    response_model=QueryResponse,
    responses={500: {"model": ErrorResponse}},
)
async def query(request: QueryRequest) -> QueryResponse:
    logger.info("Received query: %s", request.question)
    start = time.perf_counter()

    try:
        result = await _graph.ainvoke({"question": request.question})
        elapsed_ms = (time.perf_counter() - start) * 1000

        return QueryResponse(
            answer=result.get("answer", "No answer generated."),
            data=result.get("country_data", {}),
            metadata=QueryMetadata(
                country_queried=result.get("country"),
                response_time_ms=round(elapsed_ms, 2),
                cached=result.get("cached", False),
            ),
        )
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.exception("Unhandled error processing query")
        return QueryResponse(
            answer="An unexpected error occurred. Please try again.",
            data={},
            metadata=QueryMetadata(response_time_ms=round(elapsed_ms, 2)),
        )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()