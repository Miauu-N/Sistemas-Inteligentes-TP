"""
CV Analyzer — Aplicación principal Streamlit.

Entry point: streamlit run app.py
"""

import os
import sys
import tempfile

import streamlit as st

# Asegurar que src esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.styles import CUSTOM_CSS
from src.ui.components import (
    render_header,
    render_metric_card,
    render_score_gauge,
    render_skill_tags,
    render_gap_card,
    render_recommendation_card,
    render_step_progress,
)
from src.graph.builder import cv_analysis_graph


# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="CV Analyzer — Análisis Inteligente de CV",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inyectar CSS custom
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Estado de la sesión
# ---------------------------------------------------------------------------

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "is_analyzing" not in st.session_state:
    st.session_state.is_analyzing = False


# ---------------------------------------------------------------------------
# Función principal de análisis
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# UI: Página de carga
# ---------------------------------------------------------------------------

def render_upload_page():
    """Renderiza la página de carga del CV."""
    render_header()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Columnas centradas
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 📤 Subí tu CV en formato PDF")
        st.markdown(
            "<p style='color: #6b7280;'>El sistema analizará tu CV, buscará ofertas laborales "
            "relevantes, y generará recomendaciones personalizadas para mejorar tu empleabilidad.</p>",
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Arrastrá o seleccioná tu CV (PDF)",
            type=["pdf"],
            help="Tamaño máximo: 10 MB. Solo archivos PDF con texto seleccionable.",
        )

        if uploaded_file is not None:
            st.success(f"📄 **{uploaded_file.name}** ({uploaded_file.size / 1024:.0f} KB)")

            if st.button(
                "🚀 Analizar CV",
                type="primary",
                use_container_width=True,
            ):
                # Guardar el archivo temporalmente
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # Variables para progreso
                progress_bar = st.progress(0)
                
                # Nombres amigables y porcentajes para cada paso
                step_mapping = {
                    "intake": (10, "📥 Validando y extrayendo texto del PDF..."),
                    "extraction": (25, "📄 Analizando y estructurando datos con IA..."),
                    "job_search": (50, "🔍 Buscando ofertas laborales en el mercado (puede tardar un momento)..."),
                    "requirements_analysis": (65, "📊 Analizando tendencias y requisitos requeridos..."),
                    "gap_detection": (80, "🎯 Detectando brechas y comparando perfil..."),
                    "recommendations": (90, "💡 Generando plan de recomendaciones..."),
                    "report_generation": (98, "📝 Construyendo el informe final..."),
                    "error_handler": (100, "❌ Error en el proceso...")
                }

                # Ejecutar análisis con status
                with st.status(
                    "🔄 Iniciando análisis inteligente...", expanded=True
                ) as status:
                    try:
                        initial_state = {
                            "pdf_path": tmp_path,
                            "errors": [],
                            "retry_count": 0,
                        }
                        
                        final_state = None
                        
                        # Streaming del grafo para actualizar en tiempo real
                        for current_state in cv_analysis_graph.stream(initial_state, stream_mode="values"):
                            final_state = current_state
                            step = current_state.get("current_step", "")
                            
                            if step in step_mapping:
                                pct, msg = step_mapping[step]
                                progress_bar.progress(pct)
                                status.update(label=msg)
                                st.write(msg)

                        result = final_state

                        # Actualizar status final
                        errors = result.get("errors", [])
                        if errors and not result.get("final_report", {}).get("matching_score"):
                            progress_bar.progress(100)
                            status.update(
                                label="❌ Error en el análisis",
                                state="error",
                            )
                            for error in errors:
                                st.error(error)
                        else:
                            progress_bar.progress(100)
                            status.update(
                                label="✅ Análisis completado con éxito",
                                state="complete",
                            )
                            st.session_state.analysis_result = result

                    except Exception as e:
                        progress_bar.progress(100)
                        status.update(
                            label="❌ Error inesperado",
                            state="error",
                        )
                        st.error(f"Error inesperado: {e}")

                    finally:
                        # Limpiar archivo temporal
                        try:
                            os.unlink(tmp_path)
                        except OSError:
                            pass

                # Rerun para mostrar resultados
                if st.session_state.analysis_result:
                    st.rerun()

        # Features highlight
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("### ✨ ¿Qué hace CV Analyzer?")

        feat_cols = st.columns(3)

        with feat_cols[0]:
            st.markdown(
                """
                **📄 Extracción inteligente**

                Extrae automáticamente habilidades, tecnologías,
                experiencia, educación e idiomas de tu CV.
                """
            )

        with feat_cols[1]:
            st.markdown(
                """
                **🔍 Análisis de mercado**

                Busca ofertas laborales relevantes y analiza
                los requisitos más demandados del mercado.
                """
            )

        with feat_cols[2]:
            st.markdown(
                """
                **💡 Recomendaciones**

                Detecta brechas y genera recomendaciones
                personalizadas para mejorar tu perfil.
                """
            )


# ---------------------------------------------------------------------------
# UI: Página de resultados
# ---------------------------------------------------------------------------

def render_report_page():
    """Renderiza la página del informe final."""
    result = st.session_state.analysis_result
    report = result.get("final_report", {})

    if not report:
        st.error("No hay informe disponible.")
        return

    # Header
    render_header()

    # Botón para nuevo análisis
    col_back, col_spacer = st.columns([1, 4])
    with col_back:
        if st.button("← Nuevo análisis"):
            st.session_state.analysis_result = None
            st.rerun()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # --- Resumen Ejecutivo ---
    st.markdown("## 📋 Resumen Ejecutivo")
    executive_summary = report.get("executive_summary", "")
    if executive_summary:
        st.markdown(
            f"<div class='executive-summary'>{executive_summary}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # --- Métricas principales ---
    cv_summary = report.get("cv_summary", {})
    matching_score = report.get("matching_score", 0.0)
    total_jobs = report.get("total_jobs_analyzed", 0)
    total_gaps = len(report.get("gaps", []))
    total_recs = len(report.get("recommendations", []))

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric_card("Ofertas analizadas", str(total_jobs))
    with metric_cols[1]:
        render_metric_card(
            "Skills detectados",
            str(cv_summary.get("total_skills", 0)),
        )
    with metric_cols[2]:
        render_metric_card("Brechas encontradas", str(total_gaps))
    with metric_cols[3]:
        render_metric_card("Recomendaciones", str(total_recs))

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # --- Score de Match + Perfil del CV (side by side) ---
    col_score, col_profile = st.columns([1, 2])

    with col_score:
        st.markdown("### 🎯 Alineación con el mercado")
        render_score_gauge(matching_score)

    with col_profile:
        st.markdown("### 👤 Perfil del CV")

        name = cv_summary.get("name", "No disponible")
        seniority = cv_summary.get("seniority", "No determinado")
        location = cv_summary.get("location", "No especificada")

        st.markdown(f"**Nombre:** {name}")
        st.markdown(f"**Seniority:** {seniority}")
        st.markdown(f"**Ubicación:** {location}")

        if cv_summary.get("job_titles"):
            st.markdown("**Perfiles inferidos:**")
            render_skill_tags(cv_summary["job_titles"])

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # --- Skills y Tecnologías ---
    col_skills, col_tech = st.columns(2)

    with col_skills:
        st.markdown("### 🔧 Skills detectados")
        skills = cv_summary.get("skills", [])
        if skills:
            render_skill_tags(skills, "success")
        else:
            st.info("No se detectaron skills")

    with col_tech:
        st.markdown("### 💻 Tecnologías")
        technologies = cv_summary.get("technologies", [])
        if technologies:
            render_skill_tags(technologies)
        else:
            st.info("No se detectaron tecnologías")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # --- Fortalezas ---
    strengths = report.get("strengths", [])
    if strengths:
        st.markdown("### 💪 Fortalezas")
        st.markdown(
            "Competencias de tu CV que son **valoradas por el mercado**:"
        )
        render_skill_tags(strengths, "success")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # --- Brechas ---
    gaps = report.get("gaps", [])
    if gaps:
        st.markdown(f"### 🎯 Brechas detectadas ({len(gaps)})")
        st.markdown(
            "Competencias o requisitos que el mercado demanda y que podrías desarrollar:"
        )

        for gap in gaps:
            render_gap_card(gap)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # --- Recomendaciones ---
    recommendations = report.get("recommendations", [])
    if recommendations:
        st.markdown(f"### 💡 Recomendaciones personalizadas ({len(recommendations)})")
        st.markdown(
            "Acciones concretas para mejorar tu perfil y empleabilidad:"
        )

        # Filtros
        filter_cols = st.columns(3)
        with filter_cols[0]:
            filter_priority = st.multiselect(
                "Filtrar por prioridad",
                options=["alta", "media", "baja"],
                default=["alta", "media", "baja"],
            )
        with filter_cols[1]:
            all_types = list(
                set(r.get("type", "") for r in recommendations)
            )
            filter_type = st.multiselect(
                "Filtrar por tipo",
                options=all_types,
                default=all_types,
            )

        filtered = [
            r
            for r in recommendations
            if r.get("priority") in filter_priority
            and r.get("type") in filter_type
        ]

        for i, rec in enumerate(filtered, 1):
            render_recommendation_card(rec, i)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # --- Análisis de mercado ---
    market_overview = report.get("market_overview", {})
    if market_overview:
        st.markdown("### 📊 Panorama del mercado")

        market_cols = st.columns(2)

        with market_cols[0]:
            st.markdown("**Top skills demandados:**")
            top_skills = market_overview.get("top_skills", [])
            if top_skills:
                for i, skill in enumerate(top_skills[:10], 1):
                    st.markdown(f"{i}. {skill}")

        with market_cols[1]:
            modalities = market_overview.get("modalities", {})
            if modalities:
                st.markdown("**Modalidades:**")
                for mod, count in modalities.items():
                    st.markdown(f"- {mod}: {count} ofertas")

            exp_range = market_overview.get("experience_range")
            if exp_range:
                st.markdown(f"**Experiencia más solicitada:** {exp_range}")

    # --- Ofertas de referencia ---
    job_listings = result.get("job_listings", [])
    if job_listings:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔗 Ver ofertas de referencia encontradas", expanded=False):
            st.markdown("Se analizaron las siguientes ofertas para generar este reporte (mostrando primeras 15):")
            for job in job_listings[:15]:
                title = job.get("title", "Sin título")
                company = job.get("company", "Empresa desconocida")
                url = job.get("source_url", "")
                
                if url and url.startswith("http"):
                    st.markdown(f"- [{title} - {company}]({url})")
                else:
                    st.markdown(f"- **{title}** - {company}")

    # --- Footer ---
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #9ca3af; font-size: 0.8rem;'>"
        "CV Analyzer — Trabajo Final Integrador — Seminario de Agentes Inteligentes y LLMs"
        "</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Routing principal
# ---------------------------------------------------------------------------

if st.session_state.analysis_result:
    render_report_page()
else:
    render_upload_page()
