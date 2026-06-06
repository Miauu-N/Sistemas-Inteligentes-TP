"""
Modelos Pydantic para recomendaciones e informe final.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RecommendationType(str, Enum):
    """Tipos de recomendaciones que el sistema puede generar."""

    COURSE = "curso"
    CERTIFICATION = "certificación"
    PROJECT = "proyecto_práctico"
    SKILL_DEVELOPMENT = "desarrollo_habilidad"
    CV_IMPROVEMENT = "mejora_cv"
    NETWORKING = "networking"


class Recommendation(BaseModel):
    """Una recomendación personalizada para mejorar el perfil del usuario."""

    type: RecommendationType = Field(description="Tipo de recomendación")
    title: str = Field(description="Título breve de la recomendación")
    description: str = Field(
        description="Descripción detallada de la recomendación"
    )
    priority: str = Field(
        description="Prioridad: alta / media / baja"
    )
    estimated_time: str | None = Field(
        default=None,
        description="Tiempo estimado para completar (ej: '2-4 semanas')",
    )
    resources: list[str] = Field(
        default_factory=list,
        description="URLs o nombres de plataformas/recursos sugeridos",
    )
    related_gap: str | None = Field(
        default=None,
        description="La brecha específica que esta recomendación busca cerrar",
    )


class FinalReport(BaseModel):
    """
    Estructura del informe final que se presenta en la interfaz Streamlit.
    Agrega y resume todos los análisis anteriores.
    """

    generated_at: str = Field(
        description="Timestamp de generación del informe"
    )
    candidate_name: str | None = Field(
        default=None, description="Nombre del candidato"
    )

    # --- Resumen del CV ---
    cv_summary: dict = Field(
        default_factory=dict,
        description="Resumen estructurado del CV procesado",
    )

    # --- Análisis de mercado ---
    market_overview: dict = Field(
        default_factory=dict,
        description="Resumen del análisis de mercado",
    )
    total_jobs_analyzed: int = Field(
        default=0, description="Número de ofertas analizadas"
    )

    # --- Resultados del análisis ---
    matching_score: float = Field(
        default=0.0,
        description="Score de alineación CV vs mercado (0.0 - 1.0)",
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Fortalezas del candidato respecto al mercado",
    )
    gaps: list[dict] = Field(
        default_factory=list,
        description="Brechas detectadas serializadas",
    )
    recommendations: list[dict] = Field(
        default_factory=list,
        description="Recomendaciones serializadas",
    )

    # --- Resumen ejecutivo ---
    executive_summary: str = Field(
        default="",
        description="Resumen ejecutivo generado por LLM en lenguaje natural",
    )
