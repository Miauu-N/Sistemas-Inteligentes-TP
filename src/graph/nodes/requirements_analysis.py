"""
Nodo: requirements_analysis
Responsabilidad: Analizar los requisitos más frecuentes de las ofertas encontradas.
"""

from __future__ import annotations

from loguru import logger

from src.graph.state import CVAnalysisState
from src.tools.llm_tools import analyze_requirements_with_llm


def requirements_analysis_node(state: CVAnalysisState) -> dict:
    """
    Analiza las ofertas laborales y extrae un perfil de demanda del mercado.

    Lee: job_listings
    Escribe: market_requirements, current_step, errors
    """
    logger.info("=== NODO: requirements_analysis — Análisis de requisitos ===")

    job_listings = state.get("job_listings", [])
    errors = list(state.get("errors", []))

    if not job_listings:
        errors.append("No hay ofertas laborales para analizar.")
        return {
            "market_requirements": {},
            "current_step": "requirements_analysis",
            "errors": errors,
        }

    try:
        market_requirements = analyze_requirements_with_llm(
            job_listings=job_listings,
            total=len(job_listings),
        )

        logger.info(
            "Análisis completado: {} skills requeridos, {} skills deseables",
            len(market_requirements.top_required_skills),
            len(market_requirements.top_preferred_skills),
        )

        return {
            "market_requirements": market_requirements.model_dump(),
            "current_step": "requirements_analysis",
            "errors": errors,
        }

    except Exception as e:
        logger.error("Error en análisis de requisitos: {}", e)
        errors.append(f"Error analizando requisitos del mercado: {e}")
        return {
            "market_requirements": {},
            "current_step": "requirements_analysis",
            "errors": errors,
        }
