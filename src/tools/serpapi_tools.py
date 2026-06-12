"""
Herramienta de búsqueda de empleo utilizando SerpAPI (Google Jobs).
"""

import urllib.request
import urllib.parse
import json
from loguru import logger
from src.config.settings import settings
from src.models.job_models import JobListing

def search_jobs_serpapi(query: str, location: str = "Argentina") -> list[JobListing]:
    """
    Busca ofertas laborales usando Google Jobs a través de SerpAPI.
    """
    if not settings.serpapi_api_key:
        logger.warning("Clave SerpAPI (serpapi_api_key) no configurada, cancelando búsqueda SerpAPI.")
        return []

    logger.info("Buscando en SerpAPI (Google Jobs) para query: {} en {}", query, location)
    
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "api_key": settings.serpapi_api_key,
        "hl": "es",
        "gl": "ar"
    }
    
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        jobs_results = data.get("jobs_results", [])
        listings = []
        
        for job in jobs_results:
            title = job.get("title", "Sin título")
            company = job.get("company_name", "Empresa no especificada")
            location = job.get("location", "No especificada")
            description = job.get("description", "")
            
            source_url = job.get("share_link", "")
            apply_options = job.get("apply_options", [])
            if apply_options and isinstance(apply_options, list):
                source_url = apply_options[0].get("link", source_url)
                
            source_platform = job.get("via", "Google Jobs")
            if source_platform.startswith("via "):
                source_platform = source_platform[4:]
                
            listing = JobListing(
                title=title,
                company=company,
                location=location,
                modality="remoto",
                description=description,
                source_url=source_url,
                source_platform=source_platform,
            )
            listings.append(listing)
            
        logger.info("Búsqueda SerpAPI completada: {} resultados para '{}'", len(listings), query)
        return listings
        
    except Exception as e:
        logger.error("Error en SerpAPI para query '{}': {}", query, e)
        return []
