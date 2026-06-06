"""
Modelos Pydantic para la información extraída del CV.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LanguageLevel(str, Enum):
    """Nivel de competencia en un idioma."""

    BASIC = "básico"
    INTERMEDIATE = "intermedio"
    ADVANCED = "avanzado"
    NATIVE = "nativo"


class Language(BaseModel):
    """Idioma con su nivel de competencia."""

    name: str = Field(description="Nombre del idioma (ej: Inglés, Español)")
    level: LanguageLevel = Field(description="Nivel de competencia")


class Education(BaseModel):
    """Formación académica."""

    institution: str | None = Field(default=None, description="Nombre de la institución educativa")
    degree: str | None = Field(default=None, description="Título obtenido o en curso")
    field_of_study: str | None = Field(
        default=None, description="Área de estudio (ej: Ingeniería en Sistemas)"
    )
    start_year: int | None = Field(default=None, description="Año de inicio")
    end_year: int | None = Field(
        default=None, description="Año de finalización (None si en curso)"
    )
    is_completed: bool = Field(default=True, description="Si la formación está completa")


class WorkExperience(BaseModel):
    """Experiencia laboral."""

    company: str | None = Field(default=None, description="Nombre de la empresa")
    position: str | None = Field(default=None, description="Cargo o puesto")
    description: str | None = Field(
        default=None, description="Descripción de responsabilidades y logros"
    )
    start_date: str | None = Field(
        default=None, description="Fecha de inicio (formato libre)"
    )
    end_date: str | None = Field(
        default=None, description="Fecha de fin (None si es actual)"
    )
    technologies: list[str] = Field(
        default_factory=list, description="Tecnologías utilizadas en el puesto"
    )
    is_current: bool = Field(default=False, description="Si es el puesto actual")


class Project(BaseModel):
    """Proyecto personal o académico."""

    name: str | None = Field(default=None, description="Nombre del proyecto")
    description: str | None = Field(default=None, description="Descripción del proyecto")
    technologies: list[str] = Field(
        default_factory=list, description="Tecnologías utilizadas"
    )
    url: str | None = Field(
        default=None, description="URL del proyecto (GitHub, etc.)"
    )


class CVData(BaseModel):
    """
    Modelo principal con toda la información estructurada extraída del CV.
    Este modelo es la salida del nodo de extracción.
    """

    # --- Datos personales ---
    full_name: str | None = Field(default=None, description="Nombre completo")
    email: str | None = Field(default=None, description="Email de contacto")
    phone: str | None = Field(default=None, description="Teléfono de contacto")
    location: str | None = Field(
        default=None, description="Ubicación (ciudad, país)"
    )
    linkedin_url: str | None = Field(default=None, description="URL de LinkedIn")
    portfolio_url: str | None = Field(
        default=None, description="URL de portfolio o sitio personal"
    )
    summary: str | None = Field(
        default=None,
        description="Resumen profesional o extracto del CV",
    )

    # --- Competencias ---
    skills: list[str] = Field(
        default_factory=list,
        description="Habilidades técnicas (ej: Python, SQL, Machine Learning)",
    )
    technologies: list[str] = Field(
        default_factory=list,
        description="Tecnologías y herramientas específicas (ej: Docker, AWS, React)",
    )
    soft_skills: list[str] = Field(
        default_factory=list,
        description="Habilidades blandas (ej: liderazgo, trabajo en equipo)",
    )

    # --- Formación y experiencia ---
    languages: list[Language] = Field(
        default_factory=list, description="Idiomas con nivel"
    )
    education: list[Education] = Field(
        default_factory=list, description="Formación académica"
    )
    work_experience: list[WorkExperience] = Field(
        default_factory=list, description="Experiencia laboral"
    )
    projects: list[Project] = Field(
        default_factory=list, description="Proyectos personales o académicos"
    )
    certifications: list[str] = Field(
        default_factory=list, description="Certificaciones obtenidas"
    )

    # --- Inferencias ---
    inferred_seniority: str | None = Field(
        default=None,
        description="Nivel de seniority inferido: junior / semi-senior / senior",
    )
    inferred_job_titles: list[str] = Field(
        default_factory=list,
        description="Títulos de puesto inferidos a partir del perfil",
    )
