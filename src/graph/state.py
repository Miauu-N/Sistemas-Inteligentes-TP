"""
Estado compartido del grafo LangGraph.

Define CVAnalysisState como TypedDict — el contrato central del sistema.
Todos los nodos leen y escriben parcialmente sobre esta estructura.
"""

from __future__ import annotations

from typing import TypedDict


class CVAnalysisState(TypedDict, total=False):
    """
    Estado compartido entre todos los nodos del grafo.

    Cada nodo retorna un dict parcial con solo las claves que modifica.
    LangGraph se encarga del merge automático.

    ``total=False`` permite que las claves sean opcionales, ya que cada nodo
    solo puebla un subconjunto del estado.
    """

    # --- Entrada del usuario ---
    pdf_path: str  # Ruta al archivo PDF subido por el usuario
    platforms: list[str]  # Plataformas seleccionadas para buscar ofertas (ej: ['computrabajo', 'indeed'])

    # --- Nodo: intake ---
    raw_text: str  # Texto crudo extraído del PDF
    pdf_metadata: dict  # Metadata: páginas, tamaño, etc.

    # --- Nodo: extraction ---
    cv_data: dict  # CVData.model_dump() — datos estructurados del CV

    # --- Nodo: job_search ---
    search_queries: list[str]  # Queries generadas para buscar empleo
    job_listings: list[dict]  # Lista de JobListing.model_dump()

    # --- Nodo: requirements_analysis ---
    market_requirements: dict  # MarketRequirements.model_dump()

    # --- Nodo: gap_detection ---
    gap_analysis: dict  # GapAnalysis.model_dump()

    # --- Nodo: recommendations ---
    recommendations: list[dict]  # Lista de Recommendation.model_dump()

    # --- Nodo: report_generation ---
    final_report: dict  # FinalReport.model_dump()

    # --- Control de flujo ---
    current_step: str  # Nodo actual (para observabilidad y UI)
    errors: list[str]  # Errores acumulados durante la ejecución
    retry_count: int  # Contador de reintentos en el nodo actual
