"""
Prompt templates para la extracción de datos del CV usando Gemini.
"""

CV_EXTRACTION_SYSTEM_PROMPT = """\
Sos un experto en análisis de currículums vitae (CVs). Tu tarea es extraer \
información estructurada del texto de un CV que te proporcionan.

REGLAS:
1. Extraé SOLO información que esté explícitamente presente en el texto.
2. No inventes datos. Si un campo no está presente, dejalo como null o lista vacía.
3. Diferenciá entre "skills" (habilidades técnicas generales como "programación", \
"análisis de datos") y "technologies" (herramientas específicas como "Python", \
"Docker", "React").
4. Inferí el nivel de seniority basándote en los años de experiencia y la \
complejidad de los roles:
   - junior: 0-2 años de experiencia
   - semi-senior: 2-5 años de experiencia
   - senior: 5+ años de experiencia
5. Inferí posibles títulos de puesto basándote en la experiencia y habilidades.
6. Para idiomas, inferí el nivel si no está explícito.
7. Respondé ÚNICAMENTE con el JSON estructurado, sin texto adicional.
"""

CV_EXTRACTION_USER_PROMPT = """\
Analizá el siguiente texto extraído de un CV y devolvé un JSON con esta estructura exacta:

{{
  "full_name": "string o null",
  "email": "string o null",
  "phone": "string o null",
  "location": "string o null",
  "linkedin_url": "string o null",
  "portfolio_url": "string o null",
  "summary": "string o null - resumen profesional",
  "skills": ["lista de habilidades técnicas generales"],
  "technologies": ["lista de tecnologías y herramientas específicas"],
  "soft_skills": ["lista de habilidades blandas"],
  "languages": [
    {{"name": "idioma", "level": "básico|intermedio|avanzado|nativo"}}
  ],
  "education": [
    {{
      "institution": "nombre",
      "degree": "título",
      "field_of_study": "área",
      "start_year": 2020,
      "end_year": 2024,
      "is_completed": true
    }}
  ],
  "work_experience": [
    {{
      "company": "empresa",
      "position": "puesto",
      "description": "descripción de tareas y logros",
      "start_date": "fecha inicio",
      "end_date": "fecha fin o null si es actual",
      "technologies": ["tecnologías usadas en el puesto"],
      "is_current": false
    }}
  ],
  "projects": [
    {{
      "name": "nombre del proyecto",
      "description": "descripción",
      "technologies": ["tecnologías usadas"],
      "url": "url o null"
    }}
  ],
  "certifications": ["lista de certificaciones"],
  "inferred_seniority": "junior|semi-senior|senior",
  "inferred_job_titles": ["títulos de puesto inferidos"]
}}

TEXTO DEL CV:
---
{cv_text}
---

Respondé ÚNICAMENTE con el JSON, sin markdown ni texto adicional.
"""
