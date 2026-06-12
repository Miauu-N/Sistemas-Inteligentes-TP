import os
import uuid
import tempfile
import asyncio
import json
from typing import Dict, Any

from loguru import logger
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from fastapi import Depends

from src.graph.builder import cv_analysis_graph
from src.tools.pdf_generator import generate_pdf_report
from src.api.auth import get_current_user
from src.db.models import User, CVAnalysis
from src.db.database import AsyncSessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(
    title="CV Analyzer API",
    description="API REST para análisis inteligente de currículums usando LangGraph y Gemini.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes para desarrollo (ajustar en prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento en memoria para los trabajos asíncronos (jobs)
# En producción, esto debería ser Redis o una base de datos.
jobs: Dict[str, Dict[str, Any]] = {}


@app.post("/api/analyze")
async def start_analysis(
    file: UploadFile = File(...),
    platforms: str = Form(default='["computrabajo"]'),
    search_mode: str = Form(default="scraping"),
    current_user: User = Depends(get_current_user)
):
    """
    Recibe un PDF, lo guarda temporalmente y devuelve un ID de trabajo (job_id).
    Requiere autenticación JWT.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
    if search_mode == "serpapi" and not settings.serpapi_api_key:
        raise HTTPException(
            status_code=400,
            detail="La búsqueda con SerpAPI no está disponible porque la API Key no ha sido configurada en el servidor."
        )

    # Procesar las plataformas
    logger.info("Plataformas recibidas en la API: {}", platforms)
    try:
        parsed_platforms = json.loads(platforms)
        if not isinstance(parsed_platforms, list):
            parsed_platforms = [platforms]
    except Exception:
        # Fallback si se envía separado por comas o texto plano
        parsed_platforms = [p.strip() for p in platforms.split(",") if p.strip()]
        
    logger.info("Plataformas procesadas: {}", parsed_platforms)
    
    job_id = str(uuid.uuid4())
    
    # Guardar archivo temporal
    fd, path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, 'wb') as f:
        f.write(await file.read())
        
    jobs[job_id] = {
        "user_id": current_user.id,
        "pdf_path": path,
        "platforms": parsed_platforms,
        "search_mode": search_mode,
        "status": "pending",
        "result": None,
        "errors": []
    }
    
    return {"job_id": job_id, "status": "pending"}


@app.get("/api/stream/{job_id}")
async def stream_analysis(job_id: str):
    """
    Establece una conexión Server-Sent Events (SSE) para enviar el progreso 
    en tiempo real del LangGraph.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
        
    job = jobs[job_id]
    
    # Si ya se completó o falló, podemos simplemente enviar el estado final y cerrar
    if job["status"] in ["completed", "error"]:
        async def quick_generator():
            yield {
                "event": "complete" if job["status"] == "completed" else "error",
                "data": json.dumps({"status": job["status"]})
            }
        return EventSourceResponse(quick_generator())
        
    async def event_generator():
        initial_state = {
            "pdf_path": job.get("pdf_path", ""),
            "platforms": job.get("platforms", ["computrabajo"]),
            "errors": [],
            "retry_count": 0,
            "is_rescan": job.get("is_rescan", False),
            "search_mode": job.get("search_mode", "scraping"),
        }
        if job.get("is_rescan"):
            initial_state["cv_data"] = job.get("cv_data", {})
        
        try:
            job["status"] = "running"
            
            # Mapeo de nodos a mensajes para frontend
            step_mapping = {
                "intake": "Validando y extrayendo texto del PDF...",
                "extraction": "Analizando y estructurando datos con IA...",
                "job_search": "Buscando ofertas laborales en el mercado (puede tardar un momento)...",
                "requirements_analysis": "Analizando tendencias y requisitos requeridos...",
                "gap_detection": "Detectando brechas y comparando perfil...",
                "recommendations": "Generando plan de recomendaciones...",
                "report_generation": "Construyendo el informe final...",
                "error_handler": "Error en el proceso..."
            }
            
            final_state = None
            
            # Iterar asíncronamente sobre la ejecución del grafo
            # Nota: .astream requiere que el sistema subyacente soporte async
            # LangGraph se encarga de envolver los nodos síncronos en threads si es necesario
            async for state in cv_analysis_graph.astream(initial_state, stream_mode="values"):
                final_state = state
                step = state.get("current_step", "")
                
                if step in step_mapping:
                    msg = step_mapping[step]
                    # Enviar actualización de progreso
                    yield {
                        "event": "progress",
                        "data": json.dumps({
                            "step": step,
                            "message": msg
                        })
                    }
                    
            # Revisar si hubo errores irrecuperables
            errors = final_state.get("errors", [])
            if errors and not final_state.get("final_report", {}).get("matching_score"):
                job["status"] = "error"
                job["errors"] = errors
                yield {
                    "event": "error",
                    "data": json.dumps({"errors": errors})
                }
            else:
                # Todo finalizó correctamente
                job["status"] = "completed"
                report_dict = final_state.get("final_report", {})
                if isinstance(report_dict, dict):
                    report_dict = {**report_dict, "job_listings": final_state.get("job_listings", [])}
                job["result"] = report_dict
                
                # Persistir en la Base de Datos
                cv_data = final_state.get("cv_data", {})
                parsed_skills = cv_data
                job_titles = cv_data.get("inferred_job_titles", [])
                
                async with AsyncSessionLocal() as session:

                    db_analysis = CVAnalysis(
                        id=job_id,
                        user_id=job["user_id"],
                        parsed_skills=parsed_skills,
                        job_titles=job_titles,
                        final_report=report_dict
                    )
                    session.add(db_analysis)
                    await session.commit()
                
                yield {
                    "event": "complete",
                    "data": json.dumps({"status": "success"})
                }
                
        except Exception as e:
            job["status"] = "error"
            error_msg = f"Error inesperado: {str(e)}"
            job["errors"].append(error_msg)
            yield {
                "event": "error",
                "data": json.dumps({"errors": [error_msg]})
            }
        finally:
            # Limpiar archivo temporal al terminar
            try:
                if job.get("pdf_path") and os.path.exists(job["pdf_path"]):
                    os.unlink(job["pdf_path"])
            except OSError:
                pass
                
    return EventSourceResponse(event_generator())


@app.get("/api/report/{job_id}")
async def get_report(job_id: str):
    """Obtener el reporte final estructurado en JSON."""
    if job_id in jobs:
        job = jobs[job_id]
        if job["status"] == "error":
            return {"status": "error", "errors": job["errors"]}
        if job["status"] != "completed":
            return {"status": job["status"], "message": "El análisis aún no ha terminado"}
        return {"status": "completed", "report": job["result"]}
        
    # Si no está en memoria, buscar en la base de datos
    from sqlalchemy.future import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CVAnalysis).where(CVAnalysis.id == job_id))
        db_analysis = result.scalars().first()
        if db_analysis:
            return {"status": "completed", "report": db_analysis.final_report}
            
    raise HTTPException(status_code=404, detail="Trabajo no encontrado")


@app.get("/api/report/{job_id}/pdf")
async def get_report_pdf(job_id: str):
    """Descargar el reporte final en formato PDF."""
    report_data = None
    
    if job_id in jobs:
        job = jobs[job_id]
        if job["status"] == "completed":
            report_data = job["result"]
    else:
        # Buscar en la base de datos
        from sqlalchemy.future import select
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(CVAnalysis).where(CVAnalysis.id == job_id))
            db_analysis = result.scalars().first()
            if db_analysis:
                report_data = db_analysis.final_report
                
    if not report_data:
        raise HTTPException(status_code=404, detail="El reporte no existe o aún no está listo")
    pdf_path = os.path.join(tempfile.gettempdir(), f"report_{job_id}.pdf")
    
    try:
        generate_pdf_report(report_data, pdf_path)
        return FileResponse(
            pdf_path, 
            media_type="application/pdf", 
            filename="Reporte_Empleabilidad_CV.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")

# --- Endpoints de Usuario ---

@app.get("/api/users/me")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Devuelve el perfil del usuario actual, incluyendo preferencias."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "email_notifications_enabled": current_user.email_notifications_enabled
    }

from pydantic import BaseModel
class UserPreferences(BaseModel):
    email_notifications_enabled: bool

@app.put("/api/users/preferences")
async def update_user_preferences(
    prefs: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza las preferencias de notificaciones del usuario."""
    current_user.email_notifications_enabled = prefs.email_notifications_enabled
    db.add(current_user)
    await db.commit()
    return {"status": "success", "email_notifications_enabled": current_user.email_notifications_enabled}


# --- Endpoints de Historial y Re-escaneo ---

@app.get("/api/analysis/latest")
async def get_latest_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el análisis más reciente del usuario autenticado."""
    from sqlalchemy.future import select
    result = await db.execute(
        select(CVAnalysis)
        .where(CVAnalysis.user_id == current_user.id)
        .order_by(CVAnalysis.created_at.desc())
    )
    db_analysis = result.scalars().first()
    if not db_analysis:
        return {"status": "not_found", "message": "No se encontró ningún análisis previo."}
        
    return {
        "status": "completed",
        "job_id": db_analysis.id,
        "report": db_analysis.final_report,
        "completed_recommendations": db_analysis.completed_recommendations or []
    }


class RescanRequest(BaseModel):
    platforms: list[str] = ["computrabajo"]
    search_mode: str = "scraping"

@app.post("/api/analyze/rescan")
async def start_rescan(
    req: RescanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia una nueva búsqueda de ofertas usando el CV ya analizado.
    """
    from sqlalchemy.future import select
    result = await db.execute(
        select(CVAnalysis)
        .where(CVAnalysis.user_id == current_user.id)
        .order_by(CVAnalysis.created_at.desc())
    )
    db_analysis = result.scalars().first()
    if not db_analysis or not db_analysis.parsed_skills:
        raise HTTPException(status_code=400, detail="No existe un análisis previo para re-escanear.")

    if req.search_mode == "serpapi" and not settings.serpapi_api_key:
        raise HTTPException(
            status_code=400,
            detail="La búsqueda con SerpAPI no está disponible porque la API Key no ha sido configurada en el servidor."
        )

    job_id = str(uuid.uuid4())
    
    # El trabajo asíncrono tiene la bandera is_rescan=True y copia la info del CV
    jobs[job_id] = {
        "user_id": current_user.id,
        "is_rescan": True,
        "cv_data": db_analysis.parsed_skills,
        "platforms": req.platforms,
        "search_mode": req.search_mode,
        "status": "pending",
        "result": None,
        "errors": []
    }
    
    return {"job_id": job_id, "status": "pending"}


class RecommendationUpdate(BaseModel):
    index: int
    completed: bool

@app.patch("/api/analysis/{job_id}/recommendations")
async def update_recommendation_status(
    job_id: str,
    update: RecommendationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marca o desmarca una recomendación (acción) como completada."""
    from sqlalchemy.future import select
    result = await db.execute(
        select(CVAnalysis)
        .where(CVAnalysis.id == job_id, CVAnalysis.user_id == current_user.id)
    )
    db_analysis = result.scalars().first()
    if not db_analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
        
    completed = list(db_analysis.completed_recommendations or [])
    if update.completed:
        if update.index not in completed:
            completed.append(update.index)
    else:
        if update.index in completed:
            completed.remove(update.index)
            
    db_analysis.completed_recommendations = completed
    db.add(db_analysis)
    await db.commit()
    
    return {"status": "success", "completed_recommendations": db_analysis.completed_recommendations}

