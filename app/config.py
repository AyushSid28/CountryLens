from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key:str
    log_level:str="INFO"
    cache_ttl:int=300
    cache_max_size:int=128
    rest_countries_base_url:str="https://restcountries.com/v3.1"
    api_retry_max_attempts:int=5
    api_retry_base_delay:float=1.0

    model_config={"env_file":".env","extra":"ignore"}

@lru_cache
def get_settings()->Settings:
    return Settings()


