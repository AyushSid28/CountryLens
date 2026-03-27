from pydantic import BaseModel,Field
from typing import Any

class QueryRequest(BaseModel):
    question:str=Field(...,min_length=1,max_length=500,description="Question about a country")


class QueryMetadata(BaseModel):
    country_queried:str | None=None
    response_time_ms:float
    cached: bool=False
    model: str="llama-3.3-70b-versatile"

class QueryResponse(BaseModel):
    answer:str
    data:dict[str,Any]=Field(default_fctory=dict)


class HealthResponse(BaseModel):
    status:str="healthy"
    version:str="1.0.0"

class ErrorResponse(BaseModel):
    error:str
    detail:str | None=None