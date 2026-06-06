"""
Nodo: job_search
Responsabilidad: Buscar ofertas laborales relevantes al perfil del usuario.
"""

from __future__ import annotations

from loguru import logger

from src.graph.state import CVAnalysisState
from src.models.cv_models import CVData
from src.tools.llm_tools import generate_search_queries
from src.tools.scraping_tools import search_jobs_computrabajo, get_mock_job_listings
from src.config.settings import settings


def job_search_node(state: CVAnalysisState) -> dict:
    """
    Genera queries de búsqueda y scrapea ofertas laborales.

    Lee: cv_data
    Escribe: search_queries, job_listings, current_step, errors
    """
    logger.info("=== NODO: job_search — Búsqueda de ofertas laborales ===")

    cv_data_dict = state.get("cv_data", {})
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

    # Paso 2: Buscar ofertas
    all_listings = []

    for query in search_queries[:3]:  # Limitar a 3 queries
        try:
            listings = search_jobs_computrabajo(query, max_pages=settings.max_search_pages)
            all_listings.extend(listings)
            logger.info("Query '{}': {} resultados", query, len(listings))
        except Exception as e:
            logger.warning("Error scrapeando '{}': {}", query, e)

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
        
        # Agregar los mocks (también cuidando no duplicar)
        for listing in mock_listings:
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
