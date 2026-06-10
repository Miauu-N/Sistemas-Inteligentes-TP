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

from src.graph.builder import cv_analysis_graph
from src.tools.pdf_generator import generate_pdf_report

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
    platforms: str = Form(default='["computrabajo"]')
):
    """
    Recibe un PDF, lo guarda temporalmente y devuelve un ID de trabajo (job_id) 
    para suscribirse al stream de progreso.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
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
        "pdf_path": path,
        "platforms": parsed_platforms,
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
            "pdf_path": job["pdf_path"],
            "platforms": job.get("platforms", ["computrabajo"]),
            "errors": [],
            "retry_count": 0,
        }
        
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
                if os.path.exists(job["pdf_path"]):
                    os.unlink(job["pdf_path"])
            except OSError:
                pass
                
    return EventSourceResponse(event_generator())


@app.get("/api/report/{job_id}")
async def get_report(job_id: str):
    """Obtener el reporte final estructurado en JSON."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
        
    job = jobs[job_id]
    
    if job["status"] == "error":
        return {"status": "error", "errors": job["errors"]}
    
    if job["status"] != "completed":
        return {"status": job["status"], "message": "El análisis aún no ha terminado"}
        
    return {"status": "completed", "report": job["result"]}


@app.get("/api/report/{job_id}/pdf")
async def get_report_pdf(job_id: str):
    """Descargar el reporte final en formato PDF."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
        
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="El reporte aún no está listo")
        
    report_data = job["result"]
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
