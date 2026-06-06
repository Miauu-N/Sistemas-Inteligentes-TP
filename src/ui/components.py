"""
Componentes reutilizables de Streamlit para la interfaz.
"""

from __future__ import annotations

import streamlit as st


def render_header():
    """Renderiza el header principal de la aplicación."""
    st.markdown(
        """
        <div class="main-header">
            <h1>🎯 CV Analyzer</h1>
            <p>Asistente inteligente para análisis de CV y recomendación de competencias</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, col=None):
    """Renderiza una card de métrica."""
    target = col if col else st
    target.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_gauge(score: float):
    """Renderiza el gauge del matching score."""
    percentage = int(score * 100)

    if percentage >= 70:
        css_class = "score-high"
        emoji = "🟢"
        label = "Excelente alineación"
    elif percentage >= 40:
        css_class = "score-medium"
        emoji = "🟡"
        label = "Alineación moderada"
    else:
        css_class = "score-low"
        emoji = "🔴"
        label = "Oportunidad de mejora"

    st.markdown(
        f"""
        <div class="score-container">
            <div class="score-value {css_class}">{emoji} {percentage}%</div>
            <div class="score-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_tags(skills: list[str], variant: str = "default"):
    """Renderiza una lista de skills como tags."""
    css_class = {
        "default": "skill-tag",
        "success": "skill-tag skill-tag-success",
        "warning": "skill-tag skill-tag-warning",
        "danger": "skill-tag skill-tag-danger",
    }.get(variant, "skill-tag")

    tags_html = " ".join(
        f'<span class="{css_class}">{skill}</span>' for skill in skills
    )
    st.markdown(tags_html, unsafe_allow_html=True)


def render_gap_card(gap: dict):
    """Renderiza una card de brecha detectada."""
    priority = gap.get("priority", "media")
    gap_type_labels = {
        "habilidad_faltante": "🔧 Habilidad faltante",
        "experiencia_insuficiente": "📈 Experiencia insuficiente",
        "certificación_faltante": "📜 Certificación faltante",
        "idioma_faltante": "🌐 Idioma faltante",
        "brecha_educativa": "🎓 Brecha educativa",
    }

    gap_type = gap.get("gap_type", "")
    type_label = gap_type_labels.get(gap_type, gap_type)
    demand = gap.get("market_demand_percentage", 0)

    st.markdown(
        f"""
        <div class="gap-card priority-{priority}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong>{type_label}</strong>
                <span class="skill-tag skill-tag-{'danger' if priority == 'alta' else 'warning' if priority == 'media' else 'success'}">{priority.upper()}</span>
            </div>
            <div style="font-weight: 600; margin-bottom: 0.3rem;">{gap.get('skill_or_requirement', '')}</div>
            <div style="color: #6b7280; font-size: 0.9rem;">{gap.get('description', '')}</div>
            <div style="color: #9ca3af; font-size: 0.8rem; margin-top: 0.4rem;">
                📊 Demanda del mercado: {demand:.0f}% de las ofertas
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(rec: dict, index: int):
    """Renderiza una card de recomendación."""
    rec_type = rec.get("type", "")
    badge_class = f"badge-{rec_type}"

    type_emojis = {
        "curso": "📚",
        "certificación": "🏆",
        "proyecto_práctico": "💻",
        "desarrollo_habilidad": "🚀",
        "mejora_cv": "📝",
        "networking": "🤝",
    }

    emoji = type_emojis.get(rec_type, "💡")
    resources = rec.get("resources", [])
    resources_html = ""
    if resources:
        resources_html = "<div style='margin-top: 0.5rem;'>"
        for r in resources:
            if r.startswith("http"):
                resources_html += f"<a href='{r}' target='_blank' style='color: #667eea; text-decoration: none; font-size: 0.85rem;'>🔗 {r[:50]}...</a><br>"
            else:
                resources_html += f"<span style='font-size: 0.85rem; color: #6b7280;'>📌 {r}</span><br>"
        resources_html += "</div>"

    st.markdown(
        f"""
        <div class="rec-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                <div>
                    <span class="rec-type-badge {badge_class}">{emoji} {rec_type.replace('_', ' ')}</span>
                    <span class="skill-tag skill-tag-{'danger' if rec.get('priority') == 'alta' else 'warning' if rec.get('priority') == 'media' else 'success'}" style="margin-left: 0.5rem;">{rec.get('priority', 'media')}</span>
                </div>
                {f"<span style='font-size: 0.8rem; color: #9ca3af;'>⏱ {rec.get('estimated_time', '')}</span>" if rec.get('estimated_time') else ''}
            </div>
            <h4 style="margin: 0.5rem 0 0.3rem 0; font-size: 1.05rem;">{index}. {rec.get('title', '')}</h4>
            <p style="color: #4b5563; font-size: 0.9rem; line-height: 1.6;">{rec.get('description', '')}</p>
            {f"<div style='font-size: 0.8rem; color: #9ca3af; margin-top: 0.3rem;'>🎯 Cierra brecha: {rec.get('related_gap', '')}</div>" if rec.get('related_gap') else ''}
            {resources_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_progress(current_step: str):
    """Renderiza la barra de progreso con pasos."""
    steps = [
        ("intake", "📥", "Recepción"),
        ("extraction", "📄", "Extracción"),
        ("job_search", "🔍", "Búsqueda"),
        ("requirements_analysis", "📊", "Análisis"),
        ("gap_detection", "🎯", "Brechas"),
        ("recommendations", "💡", "Recomen."),
        ("report_generation", "📝", "Informe"),
    ]

    step_names = [s[0] for s in steps]

    if current_step in step_names:
        current_index = step_names.index(current_step)
    else:
        current_index = -1

    cols = st.columns(len(steps))

    for i, (step_name, emoji, label) in enumerate(steps):
        with cols[i]:
            if i < current_index:
                status = "✅"
            elif i == current_index:
                status = "⏳"
            else:
                status = "⬜"

            st.markdown(
                f"<div style='text-align: center;'>"
                f"<div style='font-size: 1.5rem;'>{status}</div>"
                f"<div style='font-size: 0.7rem; color: #6b7280;'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
