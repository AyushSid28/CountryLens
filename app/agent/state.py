from typing import Any,TypedDict



class AgentState(TypedDict):
    question:str
    country:str
    intent:str
    country_data:dict[str,Any]
    answer:str
    error:str | None=None
    cached:bool




