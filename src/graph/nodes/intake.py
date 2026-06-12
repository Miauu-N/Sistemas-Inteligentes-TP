"""
Nodo: intake
Responsabilidad: Validar el PDF y extraer texto crudo.
"""

from __future__ import annotations

from loguru import logger

from src.graph.state import CVAnalysisState
from src.tools.pdf_tools import validate_pdf, extract_pdf_text, PDFValidationError


def intake_node(state: CVAnalysisState) -> dict:
    """
    Valida el PDF subido y extrae el texto crudo.

    Lee: pdf_path
    Escribe: raw_text, pdf_metadata, current_step, errors
    """
    logger.info("=== NODO: intake — Validación y extracción de PDF ===")

    if state.get("is_rescan"):
        logger.info("Modo re-escaneo: Saltando validación y extracción de PDF.")
        return {
            "current_step": "intake",
        }

    pdf_path = state.get("pdf_path", "")
    errors = list(state.get("errors", []))

    try:
        # Paso 1: Validar el PDF
        pdf_metadata = validate_pdf(pdf_path)

        # Paso 2: Extraer texto crudo
        raw_text = extract_pdf_text(pdf_path)

        if not raw_text.strip():
            errors.append(
                "El PDF no contiene texto extraíble. "
                "Puede ser un documento escaneado (imagen). "
                "Por favor, subí un PDF con texto seleccionable."
            )
            return {
                "raw_text": "",
                "pdf_metadata": pdf_metadata,
                "current_step": "intake",
                "errors": errors,
            }

        logger.info(
            "Intake completado: {} caracteres extraídos",
            len(raw_text),
        )

        return {
            "raw_text": raw_text,
            "pdf_metadata": pdf_metadata,
            "current_step": "intake",
            "errors": errors,
        }

    except PDFValidationError as e:
        logger.error("Error de validación del PDF: {}", e)
        errors.append(str(e))
        return {
            "raw_text": "",
            "pdf_metadata": {},
            "current_step": "intake",
            "errors": errors,
        }

    except Exception as e:
        logger.error("Error inesperado en intake: {}", e)
        errors.append(f"Error inesperado al procesar el PDF: {e}")
        return {
            "raw_text": "",
            "pdf_metadata": {},
            "current_step": "intake",
            "errors": errors,
        }
