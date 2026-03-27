import httpx
import asyncio
import logging
from typing import Any
from cachetools import TTLCache
from app.config import get_settings


logger=logging.getLogger(__name__)

class CountryAPIError(Exception):
    pass

class CountryNotFoundError(CountAPIError):
    pass

def _build_cache()-> TTLCache:
    settings=get_settings()
    return TTLCache(maxsize=settings.cache_max_size,ttl=settings.cache_ttl)


_cache: TTLCache=None

def _get_cache()->TTLCache:
    global _cache
    if _cache is None:
        _cache=_build_cache()
    return _cache


async def fetch_country(country_name:str)->tuple[dict[str,Any],bool]:
    cache=_get_cache()
    cache_key=country_name.lower().strip()
    
    if cache_key in cache:
        logger.info("Cache hit for country: %s",country_name)
        return cache[cache_key],True

    
    logger.info("Cache miss for country: %s",country_name)
    data=await _call_with_retry(cache_key)
    cache[cache_key]=data
    return data,False

async def _call_with_retry(country_name:str)->dict[str,Any]:
    settings=get_settings()
    last_exc:Exception | None=None
    for attempt in range(1,settings.api_retry_max_attempts+1):
        try:
            return await _call_api(country_name)
        except CountryNotFoundError as e:
            raise

        except CountryAPIError as exc:
            last_exc=exc
            if attempt==settings.api_retry_max_attempts:
                break
            delay=settings.api_retry_base_dealy*(2**(attempt-1))
            logger.warning(
                 "API attempt %d/%d failed: %s — retrying in %.1fs",
              attempt,
              settings.api_retry_max_attempts,
              exc,
              delay,
          )
            await asyncio.sleep(delay)
    raise CountryAPIError(f"Exhausted {settings.api_retry_max_attempts} retries") from last_exc

    
async def _call_api(country_name: str) -> dict[str, Any]:
  settings = get_settings()
  url = f"{settings.rest_countries_base_url}/name/{country_name}"
  async with httpx.AsyncClient(timeout=10.0) as client:
      resp = await client.get(url, params={"fullText": "false"})
  if resp.status_code == 404:
      raise CountryNotFoundError(f"Country not found: {country_name}")
  if resp.status_code != 200:
      raise CountryAPIError(
          f"REST Countries API returned {resp.status_code}: {resp.text[:200]}"
      )
  results = resp.json()
  if not results:
      raise CountryNotFoundError(f"No results for: {country_name}")
  raw = results[0]
  return {
      "name": raw.get("name", {}).get("common", "Unknown"),
      "official_name": raw.get("name", {}).get("official", "Unknown"),
      "capital": raw.get("capital", ["Unknown"]),
      "population": raw.get("population", 0),
      "area_km2": raw.get("area", 0),
      "region": raw.get("region", "Unknown"),
      "subregion": raw.get("subregion", "Unknown"),
      "languages": raw.get("languages", {}),
      "currencies": raw.get("currencies", {}),
      "timezones": raw.get("timezones", []),
      "borders": raw.get("borders", []),
      "flag_emoji": raw.get("flag", ""),
      "maps": raw.get("maps", {}),
  }


