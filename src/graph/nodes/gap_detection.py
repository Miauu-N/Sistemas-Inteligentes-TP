"""
Nodo: gap_detection
Responsabilidad: Comparar competencias del CV con los requisitos del mercado.
"""

from __future__ import annotations

from loguru import logger

from src.graph.state import CVAnalysisState
from src.models.cv_models import CVData
from src.models.analysis_models import MarketRequirements
from src.tools.llm_tools import detect_gaps_with_llm


def gap_detection_node(state: CVAnalysisState) -> dict:
    """
    Detecta brechas entre el perfil del CV y la demanda del mercado.

    Lee: cv_data, market_requirements
    Escribe: gap_analysis, current_step, errors
    """
    logger.info("=== NODO: gap_detection — Detección de brechas ===")

    cv_data_dict = state.get("cv_data", {})
    market_req_dict = state.get("market_requirements", {})
    errors = list(state.get("errors", []))

    if not cv_data_dict or not market_req_dict:
        errors.append(
            "Faltan datos del CV o del mercado para detectar brechas."
        )
        return {
            "gap_analysis": {},
            "current_step": "gap_detection",
            "errors": errors,
        }

    try:
        cv_data = CVData.model_validate(cv_data_dict)
        market_requirements = MarketRequirements.model_validate(market_req_dict)

        gap_analysis = detect_gaps_with_llm(cv_data, market_requirements)

        logger.info(
            "Brechas detectadas: {} gaps, score de match: {:.0%}",
            gap_analysis.total_gaps_found,
            gap_analysis.matching_score,
        )

        return {
            "gap_analysis": gap_analysis.model_dump(),
            "current_step": "gap_detection",
            "errors": errors,
        }

    except Exception as e:
        logger.error("Error en detección de brechas: {}", e)
        errors.append(f"Error detectando brechas: {e}")
        return {
            "gap_analysis": {},
            "current_step": "gap_detection",
            "errors": errors,
        }
