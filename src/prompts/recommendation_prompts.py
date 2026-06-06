"""
Prompt templates para detección de brechas, recomendaciones y reporte final.
"""

GAP_DETECTION_SYSTEM_PROMPT = """\
Sos un consultor de carreras profesionales experto en tecnología. Tu tarea es \
comparar las competencias de un candidato contra los requisitos del mercado \
laboral y detectar brechas de conocimiento.
"""

GAP_DETECTION_USER_PROMPT = """\
Compará el perfil del candidato con los requisitos del mercado y detectá brechas.

PERFIL DEL CANDIDATO:
- Skills: {cv_skills}
- Tecnologías: {cv_technologies}
- Idiomas: {cv_languages}
- Educación: {cv_education}
- Certificaciones: {cv_certifications}
- Seniority: {cv_seniority}

REQUISITOS DEL MERCADO (top skills demandados):
{market_skills_json}

Devolvé un JSON con esta estructura:
{{
  "total_gaps_found": N,
  "matching_score": 0.XX,
  "gaps": [
    {{
      "gap_type": "habilidad_faltante|experiencia_insuficiente|certificación_faltante|idioma_faltante|brecha_educativa",
      "description": "descripción detallada",
      "skill_or_requirement": "habilidad o requisito específico",
      "market_demand_percentage": XX.X,
      "priority": "alta|media|baja"
    }}
  ],
  "strengths": ["competencia valorada por el mercado que el candidato ya tiene"]
}}

REGLAS:
1. El matching_score va de 0.0 (sin coincidencias) a 1.0 (perfecto).
2. Usá comparación semántica, no solo textual (ej: "JS" == "JavaScript").
3. Priorizá brechas con alta demanda de mercado (>50% de ofertas).
4. Incluí al menos las fortalezas principales (skills que coinciden).
5. Respondé ÚNICAMENTE con el JSON.
"""

RECOMMENDATIONS_SYSTEM_PROMPT = """\
Sos un mentor de carrera tecnológica con experiencia en desarrollo profesional. \
Tu tarea es generar recomendaciones accionables y personalizadas para que un \
candidato cierre sus brechas de competencias y mejore su empleabilidad.
"""

RECOMMENDATIONS_USER_PROMPT = """\
Basándote en las brechas detectadas, generá recomendaciones personalizadas.

PERFIL DEL CANDIDATO:
- Nombre: {candidate_name}
- Seniority: {seniority}
- Skills actuales: {current_skills}

BRECHAS DETECTADAS:
{gaps_json}

FORTALEZAS:
{strengths}

Generá entre 5 y 8 recomendaciones. Devolvé un JSON array:
[
  {{
    "type": "curso|certificación|proyecto_práctico|desarrollo_habilidad|mejora_cv|networking",
    "title": "título breve",
    "description": "descripción detallada y accionable",
    "priority": "alta|media|baja",
    "estimated_time": "X semanas/meses",
    "resources": ["URL o plataforma sugerida"],
    "related_gap": "la brecha que cierra"
  }}
]

REGLAS:
1. Las recomendaciones deben ser concretas y accionables.
2. Incluí recursos reales (Coursera, Udemy, freeCodeCamp, YouTube, etc.).
3. Priorizá recomendaciones que cierren brechas de alta prioridad.
4. Incluí al menos una recomendación de tipo "mejora_cv".
5. Adaptá las recomendaciones al nivel de seniority del candidato.
6. Respondé ÚNICAMENTE con el JSON array.
"""

EXECUTIVE_SUMMARY_SYSTEM_PROMPT = """\
Sos un redactor profesional especializado en informes de carrera. Tu tarea es \
escribir un resumen ejecutivo claro y motivador para un candidato.
"""

EXECUTIVE_SUMMARY_USER_PROMPT = """\
Escribí un resumen ejecutivo de 3-4 párrafos para el siguiente análisis de CV.

DATOS:
- Candidato: {candidate_name}
- Score de alineación con el mercado: {matching_score:.0%}
- Ofertas analizadas: {total_jobs}
- Fortalezas principales: {strengths}
- Brechas principales: {top_gaps}
- Top 3 recomendaciones: {top_recommendations}

REGLAS:
1. Empezá con un párrafo positivo destacando las fortalezas.
2. Mencioná las brechas principales de forma constructiva (oportunidades, no deficiencias).
3. Cerrá con las recomendaciones más impactantes y un mensaje motivador.
4. Usá un tono profesional pero cercano. Escribí en español.
5. No uses markdown, solo texto plano con párrafos separados por saltos de línea.
"""
