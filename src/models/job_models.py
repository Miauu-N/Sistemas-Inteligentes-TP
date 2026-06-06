"""
Modelos Pydantic para las ofertas laborales.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class JobListing(BaseModel):
    """Oferta laboral extraída de una fuente externa."""

    title: str = Field(description="Título del puesto")
    company: str = Field(description="Nombre de la empresa")
    location: str | None = Field(
        default=None, description="Ubicación del puesto"
    )
    modality: str | None = Field(
        default=None,
        description="Modalidad de trabajo: remoto / híbrido / presencial",
    )
    description: str = Field(
        default="", description="Descripción completa de la oferta"
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Habilidades requeridas (excluyentes)",
    )
    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Habilidades deseables (no excluyentes)",
    )
    required_experience_years: int | None = Field(
        default=None, description="Años de experiencia requeridos"
    )
    salary_range: str | None = Field(
        default=None, description="Rango salarial ofrecido"
    )
    source_url: str = Field(description="URL de la oferta laboral")
    source_platform: str = Field(
        description="Plataforma de origen: linkedin, indeed, computrabajo, etc."
    )
    posted_date: str | None = Field(
        default=None, description="Fecha de publicación"
    )
