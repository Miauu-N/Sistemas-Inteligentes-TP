"""
Modelos Pydantic para el análisis de mercado y detección de brechas.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SkillFrequency(BaseModel):
    """Frecuencia de aparición de una habilidad en las ofertas analizadas."""

    skill: str = Field(description="Nombre de la habilidad o tecnología")
    count: int = Field(description="Cantidad de ofertas que la mencionan")
    percentage: float = Field(
        description="Porcentaje de ofertas que la mencionan (0-100)"
    )


class MarketRequirements(BaseModel):
    """Perfil de demanda del mercado basado en las ofertas analizadas."""

    total_listings_analyzed: int = Field(
        description="Número total de ofertas analizadas"
    )
    top_required_skills: list[SkillFrequency] = Field(
        default_factory=list,
        description="Habilidades requeridas más frecuentes, ordenadas por frecuencia",
    )
    top_preferred_skills: list[SkillFrequency] = Field(
        default_factory=list,
        description="Habilidades deseables más frecuentes, ordenadas por frecuencia",
    )
    common_experience_range: str | None = Field(
        default=None,
        description="Rango de experiencia más solicitado (ej: '3-5 años')",
    )
    common_education_level: str | None = Field(
        default=None,
        description="Nivel educativo más solicitado",
    )
    common_modalities: dict[str, int] = Field(
        default_factory=dict,
        description="Distribución de modalidades (remoto, híbrido, presencial)",
    )
    salary_summary: str | None = Field(
        default=None,
        description="Resumen de rangos salariales encontrados",
    )


# ---------------------------------------------------------------------------
# Gap Analysis
# ---------------------------------------------------------------------------


class GapType(str, Enum):
    """Tipos de brechas de competencias detectables."""

    MISSING_SKILL = "habilidad_faltante"
    LOW_EXPERIENCE = "experiencia_insuficiente"
    MISSING_CERTIFICATION = "certificación_faltante"
    MISSING_LANGUAGE = "idioma_faltante"
    EDUCATION_GAP = "brecha_educativa"


class Gap(BaseModel):
    """Una brecha individual detectada entre el CV y los requisitos del mercado."""

    gap_type: GapType = Field(description="Tipo de brecha")
    description: str = Field(description="Descripción detallada de la brecha")
    skill_or_requirement: str = Field(
        description="La habilidad o requisito específico faltante"
    )
    market_demand_percentage: float = Field(
        description="Porcentaje de ofertas que solicitan esta competencia (0-100)"
    )
    priority: str = Field(
        description="Prioridad de la brecha: alta / media / baja"
    )


class GapAnalysis(BaseModel):
    """Resultado completo del análisis de brechas."""

    total_gaps_found: int = Field(description="Número total de brechas detectadas")
    matching_score: float = Field(
        description="Score de alineación CV vs mercado (0.0 = sin match, 1.0 = match perfecto)"
    )
    gaps: list[Gap] = Field(
        default_factory=list,
        description="Lista de brechas detectadas, ordenadas por prioridad",
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Competencias del CV que son valoradas por el mercado",
    )
