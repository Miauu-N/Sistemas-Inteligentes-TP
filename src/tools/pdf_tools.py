"""
Herramientas para procesamiento de archivos PDF.

Funciones:
    - validate_pdf: Valida formato, tamaño y número de páginas.
    - extract_pdf_text: Extrae texto crudo del PDF usando PyMuPDF.
"""

from __future__ import annotations

import os
from pathlib import Path

import fitz  # PyMuPDF

from loguru import logger

from src.config.settings import settings


class PDFValidationError(Exception):
    """Error de validación del PDF."""

    pass


def validate_pdf(pdf_path: str) -> dict:
    """
    Valida que el archivo PDF sea procesable.

    Verificaciones:
        - El archivo existe
        - La extensión es .pdf
        - El tamaño no excede el máximo configurado
        - El número de páginas no excede el máximo configurado
        - El archivo se puede abrir con PyMuPDF

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        dict con metadata del PDF: pages, size_mb, filename.

    Raises:
        PDFValidationError: Si el PDF no pasa alguna validación.
    """
    path = Path(pdf_path)

    # Verificar existencia
    if not path.exists():
        raise PDFValidationError(f"El archivo no existe: {pdf_path}")

    # Verificar extensión
    if path.suffix.lower() != ".pdf":
        raise PDFValidationError(
            f"El archivo no es un PDF. Extensión recibida: {path.suffix}"
        )

    # Verificar tamaño
    size_bytes = os.path.getsize(pdf_path)
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > settings.max_pdf_size_mb:
        raise PDFValidationError(
            f"El PDF excede el tamaño máximo ({size_mb:.1f} MB > {settings.max_pdf_size_mb} MB)"
        )

    # Verificar que se puede abrir y número de páginas
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise PDFValidationError(f"No se pudo abrir el PDF: {e}")

    num_pages = len(doc)
    doc.close()

    if num_pages > settings.max_pdf_pages:
        raise PDFValidationError(
            f"El PDF tiene demasiadas páginas ({num_pages} > {settings.max_pdf_pages})"
        )

    if num_pages == 0:
        raise PDFValidationError("El PDF no tiene páginas.")

    metadata = {
        "filename": path.name,
        "size_mb": round(size_mb, 2),
        "pages": num_pages,
    }

    logger.info(
        "PDF validado correctamente: {} ({} páginas, {:.2f} MB)",
        path.name,
        num_pages,
        size_mb,
    )

    return metadata


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extrae todo el texto del PDF usando PyMuPDF.

    Recorre todas las páginas y concatena el texto extraído.
    Si el PDF no contiene texto (ej: escaneado), retorna string vacío.

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        Texto crudo extraído del PDF.

    Raises:
        PDFValidationError: Si no se puede extraer texto.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise PDFValidationError(f"Error al abrir el PDF para extracción: {e}")

    text_parts: list[str] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text")

        if page_text.strip():
            text_parts.append(page_text)

    doc.close()

    full_text = "\n\n".join(text_parts)

    if not full_text.strip():
        logger.warning(
            "El PDF '{}' no contiene texto extraíble. "
            "Podría ser un documento escaneado.",
            Path(pdf_path).name,
        )

    logger.info(
        "Texto extraído del PDF: {} caracteres de {} páginas",
        len(full_text),
        len(text_parts),
    )

    return full_text
