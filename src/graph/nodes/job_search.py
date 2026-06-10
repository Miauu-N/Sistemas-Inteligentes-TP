"""
Nodo: job_search
Responsabilidad: Buscar ofertas laborales relevantes al perfil del usuario.
"""

from __future__ import annotations

from loguru import logger

from src.graph.state import CVAnalysisState
from src.models.cv_models import CVData
from src.tools.llm_tools import generate_search_queries
from src.tools.scraping_tools import (
    search_jobs_computrabajo,
    search_jobs_indeed,
    search_jobs_linkedin,
    search_jobs_bumeran,
    get_mock_job_listings,
)
from src.config.settings import settings


def job_search_node(state: CVAnalysisState) -> dict:
    """
    Genera queries de búsqueda y scrapea ofertas laborales.

    Lee: cv_data, platforms
    Escribe: search_queries, job_listings, current_step, errors
    """
    logger.info("=== NODO: job_search — Búsqueda de ofertas laborales ===")

    cv_data_dict = state.get("cv_data", {})
    platforms = state.get("platforms", ["computrabajo"])
    errors = list(state.get("errors", []))

    if not cv_data_dict:
        errors.append("No hay datos del CV para generar búsquedas.")
        return {
            "search_queries": [],
            "job_listings": [],
            "current_step": "job_search",
            "errors": errors,
        }

    # Reconstruir CVData desde el dict del estado
    try:
        cv_data = CVData.model_validate(cv_data_dict)
    except Exception as e:
        logger.error("Error reconstruyendo CVData: {}", e)
        errors.append(f"Error en datos del CV: {e}")
        return {
            "search_queries": [],
            "job_listings": [],
            "current_step": "job_search",
            "errors": errors,
        }

    # Paso 1: Generar queries de búsqueda
    try:
        search_queries = generate_search_queries(cv_data)
    except Exception as e:
        logger.warning("Error generando queries, usando fallback: {}", e)
        search_queries = cv_data.inferred_job_titles[:3] or ["developer"]

    # Paso 2: Buscar ofertas en las plataformas seleccionadas
    all_listings = []
    if not platforms:
        platforms = ["computrabajo"]

    for query in search_queries[:3]:  # Limitar a 3 queries
        for platform in platforms:
            try:
                if platform == "computrabajo":
                    listings = search_jobs_computrabajo(query, max_pages=settings.max_search_pages)
                    all_listings.extend(listings)
                    logger.info("Computrabajo Query '{}': {} resultados", query, len(listings))
                elif platform == "indeed":
                    listings = search_jobs_indeed(query, max_pages=settings.max_search_pages)
                    all_listings.extend(listings)
                    logger.info("Indeed Query '{}': {} resultados", query, len(listings))
                elif platform == "linkedin":
                    listings = search_jobs_linkedin(query, max_pages=1)
                    all_listings.extend(listings)
                    logger.info("LinkedIn Query '{}': {} resultados", query, len(listings))
                elif platform == "bumeran":
                    listings = search_jobs_bumeran(query, max_pages=settings.max_search_pages)
                    all_listings.extend(listings)
                    logger.info("Bumeran Query '{}': {} resultados", query, len(listings))
            except Exception as e:
                logger.warning("Error scrapeando '{}' en '{}': {}", query, platform, e)

    # Deduplicar por título + empresa y filtrar inválidos
    seen = set()
    unique_listings = []
    for listing in all_listings:
        # Ignorar ofertas sin título real
        if not listing.title or listing.title.strip() == "":
            continue
            
        key = f"{listing.title.lower()}|{listing.company.lower()}"
        if key not in seen:
            seen.add(key)
            unique_listings.append(listing)

    # Solo inyectar mocks si la búsqueda real falló categóricamente (< 2 resultados únicos)
    if len(unique_listings) < 2:
        logger.info(
            "Solo {} ofertas reales únicas encontradas. Agregando datos de respaldo.",
            len(unique_listings),
        )
        primary_title = (
            cv_data.inferred_job_titles[0]
            if cv_data.inferred_job_titles
            else "Desarrollador Python"
        )
        mock_listings = get_mock_job_listings(primary_title)
        
        # Adaptar las plataformas de origen en los mocks a lo que el usuario seleccionó
        target_platform = platforms[0] if platforms else "computrabajo"
        
        # Agregar los mocks (también cuidando no duplicar)
        for listing in mock_listings:
            listing.is_mock = True
            listing.source_platform = target_platform
            if target_platform == "indeed":
                listing.source_url = f"https://ar.indeed.com/jobs?q={listing.title.replace(' ', '+')}"
            elif target_platform == "computrabajo":
                listing.source_url = f"https://www.computrabajo.com.ar/trabajo-de-{listing.title.lower().replace(' ', '-')}"
            elif target_platform == "linkedin":
                listing.source_url = f"https://www.linkedin.com/jobs/search/?keywords={listing.title.replace(' ', '%20')}"
            elif target_platform == "bumeran":
                listing.source_url = f"https://www.bumeran.com.ar/empleos-busqueda-{listing.title.lower().replace(' ', '-')}.html"
                
            key = f"{listing.title.lower()}|{listing.company.lower()}"
            if key not in seen:
                seen.add(key)
                unique_listings.append(listing)

    logger.info(
        "Búsqueda completada: {} ofertas únicas (de {} totales)",
        len(unique_listings),
        len(all_listings),
    )

    return {
        "search_queries": search_queries,
        "job_listings": [l.model_dump() for l in unique_listings],
        "current_step": "job_search",
        "errors": errors,
    }
