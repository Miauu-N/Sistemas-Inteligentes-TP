"""
Nodo: recommendations
Responsabilidad: Generar recomendaciones personalizadas para cerrar brechas.
"""

from __future__ import annotations

from loguru import logger

from src.graph.state import CVAnalysisState
from src.models.cv_models import CVData
from src.models.analysis_models import GapAnalysis
from src.tools.llm_tools import generate_recommendations_with_llm


def recommendations_node(state: CVAnalysisState) -> dict:
    """
    Genera recomendaciones personalizadas basadas en el análisis de brechas.

    Lee: cv_data, gap_analysis
    Escribe: recommendations, current_step, errors
    """
    logger.info("=== NODO: recommendations — Generación de recomendaciones ===")

    cv_data_dict = state.get("cv_data", {})
    gap_analysis_dict = state.get("gap_analysis", {})
    errors = list(state.get("errors", []))

    if not cv_data_dict or not gap_analysis_dict:
        errors.append(
            "Faltan datos del CV o del análisis de brechas para generar recomendaciones."
        )
        return {
            "recommendations": [],
            "current_step": "recommendations",
            "errors": errors,
        }

    try:
        cv_data = CVData.model_validate(cv_data_dict)
        gap_analysis = GapAnalysis.model_validate(gap_analysis_dict)

        recommendations = generate_recommendations_with_llm(cv_data, gap_analysis)

        logger.info(
            "Recomendaciones generadas: {} items",
            len(recommendations),
        )

        return {
            "recommendations": [r.model_dump() for r in recommendations],
            "current_step": "recommendations",
            "errors": errors,
        }

    except Exception as e:
        logger.error("Error generando recomendaciones: {}", e)
        errors.append(f"Error generando recomendaciones: {e}")
        return {
            "recommendations": [],
            "current_step": "recommendations",
            "errors": errors,
        }
