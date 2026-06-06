"""
Herramientas que interactúan con Gemini (LLM) a través de LangChain.

Incluye funciones para:
    - parse_cv_with_llm: Extracción estructurada de datos del CV.
    - generate_search_queries: Generación de queries de búsqueda.
    - analyze_requirements_with_llm: Análisis de requisitos del mercado.
    - detect_gaps_with_llm: Detección de brechas.
    - generate_recommendations_with_llm: Generación de recomendaciones.
    - generate_executive_summary: Resumen ejecutivo.
"""

from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from src.config.settings import settings
from src.models.cv_models import CVData
from src.models.analysis_models import MarketRequirements, GapAnalysis
from src.models.report_models import Recommendation
from src.prompts.extraction_prompts import (
    CV_EXTRACTION_SYSTEM_PROMPT,
    CV_EXTRACTION_USER_PROMPT,
)
from src.prompts.analysis_prompts import (
    SEARCH_QUERIES_SYSTEM_PROMPT,
    SEARCH_QUERIES_USER_PROMPT,
    REQUIREMENTS_ANALYSIS_SYSTEM_PROMPT,
    REQUIREMENTS_ANALYSIS_USER_PROMPT,
)
from src.prompts.recommendation_prompts import (
    GAP_DETECTION_SYSTEM_PROMPT,
    GAP_DETECTION_USER_PROMPT,
    RECOMMENDATIONS_SYSTEM_PROMPT,
    RECOMMENDATIONS_USER_PROMPT,
    EXECUTIVE_SUMMARY_SYSTEM_PROMPT,
    EXECUTIVE_SUMMARY_USER_PROMPT,
)


def _get_llm() -> ChatGoogleGenerativeAI:
    """Crea una instancia del modelo Gemini."""
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.1,  # Baja temperatura para extracción precisa
    )


def _invoke_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Invoca al LLM con un prompt de sistema y usuario.

    Returns:
        El contenido de texto de la respuesta del LLM.
    """
    llm = _get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)
    
    content = response.content
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
            elif isinstance(block, str):
                text_parts.append(block)
        return "".join(text_parts)
    
    return str(content)


def _parse_json_response(text: str) -> dict | list:
    """
    Parsea la respuesta del LLM como JSON.

    Intenta limpiar el texto si viene envuelto en bloques de código markdown.
    """
    cleaned = text.strip()

    # Remover bloques de código markdown si están presentes
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remover primera línea (```json) y última (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    return json.loads(cleaned)


# ---------------------------------------------------------------------------
# Extracción de CV
# ---------------------------------------------------------------------------


def parse_cv_with_llm(raw_text: str) -> CVData:
    """
    Envía el texto crudo del CV a Gemini y obtiene datos estructurados.

    Args:
        raw_text: Texto crudo extraído del PDF.

    Returns:
        CVData con la información estructurada del CV.

    Raises:
        ValueError: Si el LLM no retorna JSON válido o no pasa validación.
    """
    logger.info("Enviando texto del CV a Gemini para extracción estructurada...")

    user_prompt = CV_EXTRACTION_USER_PROMPT.format(cv_text=raw_text)
    response_text = _invoke_llm(CV_EXTRACTION_SYSTEM_PROMPT, user_prompt)

    try:
        data = _parse_json_response(response_text)
    except json.JSONDecodeError as e:
        logger.error("Error parseando JSON del LLM: {}", e)
        logger.debug("Respuesta del LLM: {}", response_text[:500])
        raise ValueError(f"El LLM no retornó JSON válido: {e}")

    # Validar con Pydantic
    try:
        cv_data = CVData.model_validate(data)
    except Exception as e:
        logger.error("Error validando CVData con Pydantic: {}", e)
        raise ValueError(f"Los datos extraídos no cumplen el schema: {e}")

    logger.info(
        "CV extraído exitosamente: {} skills, {} tecnologías, {} experiencias",
        len(cv_data.skills),
        len(cv_data.technologies),
        len(cv_data.work_experience),
    )

    return cv_data


# ---------------------------------------------------------------------------
# Generación de search queries
# ---------------------------------------------------------------------------


def generate_search_queries(cv_data: CVData) -> list[str]:
    """
    Genera queries de búsqueda optimizadas para portales de empleo.

    Args:
        cv_data: Datos estructurados del CV.

    Returns:
        Lista de 3-5 queries de búsqueda.
    """
    logger.info("Generando queries de búsqueda para el perfil...")

    user_prompt = SEARCH_QUERIES_USER_PROMPT.format(
        skills=", ".join(cv_data.skills[:10]),
        technologies=", ".join(cv_data.technologies[:10]),
        job_titles=", ".join(cv_data.inferred_job_titles),
        seniority=cv_data.inferred_seniority or "no especificado",
        location=cv_data.location or "Argentina",
    )

    response_text = _invoke_llm(SEARCH_QUERIES_SYSTEM_PROMPT, user_prompt)

    try:
        queries = _parse_json_response(response_text)
    except json.JSONDecodeError:
        logger.warning("No se pudo parsear queries del LLM, usando fallback")
        # Fallback: usar los títulos inferidos como queries
        queries = cv_data.inferred_job_titles[:3] or ["developer", "programador"]

    logger.info("Queries generadas: {}", queries)
    return queries


# ---------------------------------------------------------------------------
# Análisis de requisitos del mercado
# ---------------------------------------------------------------------------


def analyze_requirements_with_llm(
    job_listings: list[dict], total: int
) -> MarketRequirements:
    """
    Analiza las ofertas laborales y extrae requisitos frecuentes.

    Args:
        job_listings: Lista de ofertas serializadas como dicts.
        total: Número total de ofertas.

    Returns:
        MarketRequirements con el perfil de demanda.
    """
    logger.info("Analizando requisitos de {} ofertas laborales...", total)

    user_prompt = REQUIREMENTS_ANALYSIS_USER_PROMPT.format(
        job_listings_json=json.dumps(job_listings, ensure_ascii=False, indent=2),
        total=total,
    )

    response_text = _invoke_llm(
        REQUIREMENTS_ANALYSIS_SYSTEM_PROMPT, user_prompt
    )

    try:
        data = _parse_json_response(response_text)
        return MarketRequirements.model_validate(data)
    except (json.JSONDecodeError, Exception) as e:
        logger.error("Error analizando requisitos: {}", e)
        raise ValueError(f"Error en análisis de requisitos: {e}")


# ---------------------------------------------------------------------------
# Detección de brechas
# ---------------------------------------------------------------------------


def detect_gaps_with_llm(
    cv_data: CVData, market_requirements: MarketRequirements
) -> GapAnalysis:
    """
    Compara el perfil del CV contra los requisitos del mercado.

    Args:
        cv_data: Datos del CV.
        market_requirements: Requisitos del mercado.

    Returns:
        GapAnalysis con brechas y fortalezas.
    """
    logger.info("Detectando brechas entre CV y mercado...")

    # Preparar skills del mercado para el prompt
    market_skills = [
        {"skill": s.skill, "percentage": s.percentage}
        for s in market_requirements.top_required_skills
    ]

    # Preparar idiomas del CV
    cv_languages = [
        f"{l.name} ({l.level.value})" for l in cv_data.languages
    ]

    # Preparar educación del CV
    cv_education = [
        f"{e.degree} en {e.field_of_study} - {e.institution}"
        for e in cv_data.education
    ]

    user_prompt = GAP_DETECTION_USER_PROMPT.format(
        cv_skills=", ".join(cv_data.skills),
        cv_technologies=", ".join(cv_data.technologies),
        cv_languages=", ".join(cv_languages) or "No especificados",
        cv_education="; ".join(cv_education) or "No especificada",
        cv_certifications=", ".join(cv_data.certifications) or "Ninguna",
        cv_seniority=cv_data.inferred_seniority or "No determinado",
        market_skills_json=json.dumps(
            market_skills, ensure_ascii=False, indent=2
        ),
    )

    response_text = _invoke_llm(GAP_DETECTION_SYSTEM_PROMPT, user_prompt)

    try:
        data = _parse_json_response(response_text)
        return GapAnalysis.model_validate(data)
    except (json.JSONDecodeError, Exception) as e:
        logger.error("Error detectando brechas: {}", e)
        raise ValueError(f"Error en detección de brechas: {e}")


# ---------------------------------------------------------------------------
# Generación de recomendaciones
# ---------------------------------------------------------------------------


def generate_recommendations_with_llm(
    cv_data: CVData, gap_analysis: GapAnalysis
) -> list[Recommendation]:
    """
    Genera recomendaciones personalizadas para cerrar brechas.

    Args:
        cv_data: Datos del CV.
        gap_analysis: Análisis de brechas.

    Returns:
        Lista de recomendaciones.
    """
    logger.info("Generando recomendaciones personalizadas...")

    gaps_for_prompt = [
        {
            "type": g.gap_type.value,
            "skill": g.skill_or_requirement,
            "priority": g.priority,
            "demand": f"{g.market_demand_percentage:.0f}%",
        }
        for g in gap_analysis.gaps
    ]

    user_prompt = RECOMMENDATIONS_USER_PROMPT.format(
        candidate_name=cv_data.full_name or "Candidato",
        seniority=cv_data.inferred_seniority or "no determinado",
        current_skills=", ".join(cv_data.skills + cv_data.technologies),
        gaps_json=json.dumps(gaps_for_prompt, ensure_ascii=False, indent=2),
        strengths=", ".join(gap_analysis.strengths),
    )

    response_text = _invoke_llm(RECOMMENDATIONS_SYSTEM_PROMPT, user_prompt)

    try:
        data = _parse_json_response(response_text)
        return [Recommendation.model_validate(item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        logger.error("Error generando recomendaciones: {}", e)
        raise ValueError(f"Error en generación de recomendaciones: {e}")


# ---------------------------------------------------------------------------
# Resumen ejecutivo
# ---------------------------------------------------------------------------


def generate_executive_summary(
    candidate_name: str,
    matching_score: float,
    total_jobs: int,
    strengths: list[str],
    gaps: list[dict],
    recommendations: list[dict],
) -> str:
    """
    Genera un resumen ejecutivo en lenguaje natural.

    Returns:
        Texto del resumen ejecutivo.
    """
    logger.info("Generando resumen ejecutivo...")

    top_gaps = [g.get("skill_or_requirement", g.get("skill", "")) for g in gaps[:3]]
    top_recs = [r.get("title", "") for r in recommendations[:3]]

    user_prompt = EXECUTIVE_SUMMARY_USER_PROMPT.format(
        candidate_name=candidate_name or "el candidato",
        matching_score=matching_score,
        total_jobs=total_jobs,
        strengths=", ".join(strengths[:5]),
        top_gaps=", ".join(top_gaps),
        top_recommendations=", ".join(top_recs),
    )

    return _invoke_llm(EXECUTIVE_SUMMARY_SYSTEM_PROMPT, user_prompt)
