"""
Nodo: error_handler
Responsabilidad: Manejar errores críticos y generar mensajes amigables.
"""

from __future__ import annotations

from loguru import logger

from src.graph.state import CVAnalysisState


def error_handler_node(state: CVAnalysisState) -> dict:
    """
    Captura errores y genera un estado final con mensaje amigable.

    Lee: errors, current_step
    Escribe: final_report, current_step
    """
    errors = state.get("errors", [])
    current_step = state.get("current_step", "unknown")

    logger.error(
        "Error handler activado. Paso: {}. Errores: {}",
        current_step,
        errors,
    )

    error_messages = "\n".join(f"• {e}" for e in errors) if errors else "Error desconocido"

    return {
        "final_report": {
            "generated_at": "",
            "candidate_name": None,
            "cv_summary": {},
            "market_overview": {},
            "total_jobs_analyzed": 0,
            "matching_score": 0.0,
            "strengths": [],
            "gaps": [],
            "recommendations": [],
            "executive_summary": (
                f"No se pudo completar el análisis. "
                f"Se encontraron los siguientes errores:\n\n{error_messages}\n\n"
                f"Por favor, verificá el archivo PDF e intentá nuevamente."
            ),
        },
        "current_step": "error_handler",
    }
