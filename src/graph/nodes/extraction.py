"""
Nodo: extraction
Responsabilidad: Extraer datos estructurados del CV usando Gemini.
"""

from __future__ import annotations

from loguru import logger

from src.graph.state import CVAnalysisState
from src.tools.llm_tools import parse_cv_with_llm


def extraction_node(state: CVAnalysisState) -> dict:
    """
    Envía el texto crudo del CV a Gemini y obtiene datos estructurados.

    Lee: raw_text
    Escribe: cv_data, current_step, errors
    """
    logger.info("=== NODO: extraction — Extracción de datos con Gemini ===")

    raw_text = state.get("raw_text", "")
    errors = list(state.get("errors", []))
    retry_count = state.get("retry_count", 0)

    if not raw_text.strip():
        errors.append("No hay texto para procesar en el nodo de extracción.")
        return {
            "cv_data": {},
            "current_step": "extraction",
            "errors": errors,
        }

    max_retries = 2
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            cv_data = parse_cv_with_llm(raw_text)

            logger.info(
                "Extracción exitosa: nombre={}, skills={}, exp={}",
                cv_data.full_name,
                len(cv_data.skills),
                len(cv_data.work_experience),
            )

            return {
                "cv_data": cv_data.model_dump(),
                "current_step": "extraction",
                "errors": errors,
                "retry_count": 0,
            }

        except ValueError as e:
            last_error = str(e)
            logger.warning(
                "Intento {}/{} fallido en extracción: {}",
                attempt + 1,
                max_retries + 1,
                e,
            )

            if attempt < max_retries:
                logger.info("Reintentando extracción...")
                continue

        except Exception as e:
            last_error = str(e)
            logger.error("Error inesperado en extracción: {}", e)
            break

    errors.append(f"Error en la extracción de datos del CV: {last_error}")

    return {
        "cv_data": {},
        "current_step": "extraction",
        "errors": errors,
        "retry_count": retry_count + 1,
    }
