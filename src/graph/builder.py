"""
Constructor del grafo LangGraph.

Define la topología del grafo: nodos, edges y routing condicional.
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from src.graph.state import CVAnalysisState
from src.graph.nodes.intake import intake_node
from src.graph.nodes.extraction import extraction_node
from src.graph.nodes.job_search import job_search_node
from src.graph.nodes.requirements_analysis import requirements_analysis_node
from src.graph.nodes.gap_detection import gap_detection_node
from src.graph.nodes.recommendations import recommendations_node
from src.graph.nodes.report_generation import report_generation_node
from src.graph.nodes.error_handler import error_handler_node


# ---------------------------------------------------------------------------
# Funciones de routing condicional
# ---------------------------------------------------------------------------


def route_after_intake(state: CVAnalysisState) -> str:
    """
    Decide si continuar con la extracción o ir al error handler.

    Si hay errores en el estado (PDF inválido, sin texto), redirige al
    error_handler. De lo contrario, continúa con extraction.
    """
    errors = state.get("errors", [])
    raw_text = state.get("raw_text", "")

    if errors or not raw_text.strip():
        return "error_handler"
    return "extraction"


def route_after_extraction(state: CVAnalysisState) -> str:
    """
    Decide si continuar con la búsqueda o ir al error handler.

    Si la extracción falló (cv_data vacío), redirige al error_handler.
    """
    cv_data = state.get("cv_data", {})

    if not cv_data:
        return "error_handler"
    return "job_search"


# ---------------------------------------------------------------------------
# Construcción del grafo
# ---------------------------------------------------------------------------


def build_graph() -> StateGraph:
    """
    Construye y retorna el grafo LangGraph compilado.

    Topología:
        START → intake → [extraction | error_handler]
        extraction → [job_search | error_handler]
        job_search → requirements_analysis
        requirements_analysis → gap_detection
        gap_detection → recommendations
        recommendations → report_generation
        report_generation → END
        error_handler → END
    """
    # Crear grafo con el estado tipado
    workflow = StateGraph(CVAnalysisState)

    # Registrar todos los nodos
    workflow.add_node("intake", intake_node)
    workflow.add_node("extraction", extraction_node)
    workflow.add_node("job_search", job_search_node)
    workflow.add_node("requirements_analysis", requirements_analysis_node)
    workflow.add_node("gap_detection", gap_detection_node)
    workflow.add_node("recommendations", recommendations_node)
    workflow.add_node("report_generation", report_generation_node)
    workflow.add_node("error_handler", error_handler_node)

    # --- Edges ---

    # START → intake (siempre)
    workflow.add_edge(START, "intake")

    # intake → [extraction | error_handler] (condicional)
    workflow.add_conditional_edges(
        "intake",
        route_after_intake,
        {
            "extraction": "extraction",
            "error_handler": "error_handler",
        },
    )

    # extraction → [job_search | error_handler] (condicional)
    workflow.add_conditional_edges(
        "extraction",
        route_after_extraction,
        {
            "job_search": "job_search",
            "error_handler": "error_handler",
        },
    )

    # Flujo lineal: job_search → requirements → gaps → recommendations → report
    workflow.add_edge("job_search", "requirements_analysis")
    workflow.add_edge("requirements_analysis", "gap_detection")
    workflow.add_edge("gap_detection", "recommendations")
    workflow.add_edge("recommendations", "report_generation")

    # Nodos terminales
    workflow.add_edge("report_generation", END)
    workflow.add_edge("error_handler", END)

    return workflow.compile()


# Instancia global del grafo compilado
cv_analysis_graph = build_graph()
