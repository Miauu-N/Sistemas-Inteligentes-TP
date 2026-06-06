"""
Nodo: report_generation
Responsabilidad: Compilar el informe final con resumen ejecutivo.
"""

from __future__ import annotations

from datetime import datetime

from loguru import logger

from src.graph.state import CVAnalysisState
from src.models.report_models import FinalReport
from src.tools.llm_tools import generate_executive_summary


def report_generation_node(state: CVAnalysisState) -> dict:
    """
    Compila todos los análisis en un informe final.

    Lee: cv_data, market_requirements, gap_analysis, recommendations, job_listings
    Escribe: final_report, current_step
    """
    logger.info("=== NODO: report_generation — Generación del informe ===")

    cv_data = state.get("cv_data", {})
    market_requirements = state.get("market_requirements", {})
    gap_analysis = state.get("gap_analysis", {})
    recommendations = state.get("recommendations", [])
    job_listings = state.get("job_listings", [])
    errors = list(state.get("errors", []))

    # Extraer datos para el resumen ejecutivo
    candidate_name = cv_data.get("full_name", "Candidato")
    matching_score = gap_analysis.get("matching_score", 0.0)
    strengths = gap_analysis.get("strengths", [])
    gaps = gap_analysis.get("gaps", [])

    # Generar resumen ejecutivo con LLM
    try:
        executive_summary = generate_executive_summary(
            candidate_name=candidate_name,
            matching_score=matching_score,
            total_jobs=len(job_listings),
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations,
        )
    except Exception as e:
        logger.warning("Error generando resumen ejecutivo: {}", e)
        executive_summary = (
            f"Análisis completado para {candidate_name}. "
            f"Se analizaron {len(job_listings)} ofertas laborales. "
            f"Score de alineación con el mercado: {matching_score:.0%}."
        )

    # Preparar resumen del CV
    cv_summary = {
        "name": candidate_name,
        "email": cv_data.get("email"),
        "location": cv_data.get("location"),
        "seniority": cv_data.get("inferred_seniority"),
        "total_skills": len(cv_data.get("skills", [])),
        "total_technologies": len(cv_data.get("technologies", [])),
        "total_experience": len(cv_data.get("work_experience", [])),
        "total_education": len(cv_data.get("education", [])),
        "skills": cv_data.get("skills", []),
        "technologies": cv_data.get("technologies", []),
        "languages": cv_data.get("languages", []),
        "job_titles": cv_data.get("inferred_job_titles", []),
    }

    # Preparar overview del mercado
    market_overview = {
        "total_analyzed": market_requirements.get("total_listings_analyzed", 0),
        "top_skills": [
            s.get("skill", "")
            for s in market_requirements.get("top_required_skills", [])[:10]
        ],
        "experience_range": market_requirements.get("common_experience_range"),
        "modalities": market_requirements.get("common_modalities", {}),
    }

    # Construir informe final
    report = FinalReport(
        generated_at=datetime.now().isoformat(),
        candidate_name=candidate_name,
        cv_summary=cv_summary,
        market_overview=market_overview,
        total_jobs_analyzed=len(job_listings),
        matching_score=matching_score,
        strengths=strengths,
        gaps=gaps,
        recommendations=recommendations,
        executive_summary=executive_summary,
    )

    logger.info("Informe final generado exitosamente para '{}'", candidate_name)

    return {
        "final_report": report.model_dump(),
        "current_step": "report_generation",
        "errors": errors,
    }
