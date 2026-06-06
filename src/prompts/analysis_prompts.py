"""
Prompt templates para análisis de mercado y generación de search queries.
"""

SEARCH_QUERIES_SYSTEM_PROMPT = """\
Sos un experto en búsqueda de empleo y mercado laboral. Tu tarea es generar \
queries de búsqueda optimizadas para encontrar ofertas laborales relevantes \
para un candidato, basándote en su perfil profesional.
"""

SEARCH_QUERIES_USER_PROMPT = """\
Basándote en el siguiente perfil profesional, generá entre 3 y 5 queries de \
búsqueda para portales de empleo (Computrabajo, Indeed, LinkedIn).

PERFIL:
- Habilidades principales: {skills}
- Tecnologías: {technologies}
- Títulos de puesto inferidos: {job_titles}
- Nivel de seniority: {seniority}
- Ubicación: {location}

REGLAS:
1. Las queries deben ser cortas y específicas (2-4 palabras).
2. Incluí variaciones en español e inglés si aplica.
3. Priorizá los títulos de puesto más probables.
4. No uses operadores booleanos ni caracteres especiales.

Respondé ÚNICAMENTE con un JSON array de strings:
["query 1", "query 2", "query 3"]
"""

REQUIREMENTS_ANALYSIS_SYSTEM_PROMPT = """\
Sos un analista de mercado laboral experto. Tu tarea es analizar un conjunto \
de ofertas laborales y extraer los patrones de requisitos más frecuentes.
"""

REQUIREMENTS_ANALYSIS_USER_PROMPT = """\
Analizá las siguientes ofertas laborales y generá un perfil de demanda del mercado.

OFERTAS LABORALES:
{job_listings_json}

Devolvé un JSON con esta estructura:
{{
  "total_listings_analyzed": {total},
  "top_required_skills": [
    {{"skill": "nombre", "count": N, "percentage": X.X}}
  ],
  "top_preferred_skills": [
    {{"skill": "nombre", "count": N, "percentage": X.X}}
  ],
  "common_experience_range": "X-Y años o null",
  "common_education_level": "nivel o null",
  "common_modalities": {{"remoto": N, "híbrido": N, "presencial": N}},
  "salary_summary": "resumen o null"
}}

REGLAS:
1. Ordená skills por frecuencia descendente (top 15 máximo).
2. Calculá el porcentaje respecto al total de ofertas.
3. Normalizá nombres de skills (ej: "JS" → "JavaScript", "py" → "Python").
4. Respondé ÚNICAMENTE con el JSON.
"""
