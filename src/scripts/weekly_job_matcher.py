import asyncio
import os
import sys
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger

from src.db.database import AsyncSessionLocal
from src.db.models import User, CVAnalysis
from src.models.job_models import JobListing
from src.tools.scraping_tools import _scrape_computrabajo, _scrape_indeed, _scrape_linkedin
from src.config.settings import settings

# Email config
SMTP_SERVER = settings.smtp_server
SMTP_PORT = settings.smtp_port
SMTP_USERNAME = settings.smtp_username
SMTP_PASSWORD = settings.smtp_password
SENDER_EMAIL = settings.sender_email or SMTP_USERNAME


async def search_jobs_linkedin_async(query: str, max_pages: int = 1) -> list[JobListing]:
    listings = []
    try:
        raw_results = await _scrape_linkedin(query, max_pages)
        for raw in raw_results:
            try:
                listings.append(JobListing(
                    title=raw.get("title", "Sin título"),
                    company=raw.get("company", "Empresa no especificada"),
                    location=raw.get("location"),
                    modality=raw.get("modality"),
                    description=raw.get("description", ""),
                    source_url=raw.get("url", ""),
                    source_platform="linkedin",
                ))
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Error en scrape linkedin: {e}")
    return listings

async def search_jobs_indeed_async(query: str, max_pages: int = 1) -> list[JobListing]:
    listings = []
    try:
        raw_results = await _scrape_indeed(query, max_pages)
        for raw in raw_results:
            try:
                listings.append(JobListing(
                    title=raw.get("title", "Sin título"),
                    company=raw.get("company", "Empresa no especificada"),
                    location=raw.get("location"),
                    modality=raw.get("modality"),
                    description=raw.get("description", ""),
                    source_url=raw.get("url", ""),
                    source_platform="indeed",
                ))
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Error en scrape indeed: {e}")
    return listings

async def search_jobs_computrabajo_async(query: str, max_pages: int = 1) -> list[JobListing]:
    listings = []
    try:
        raw_results = await _scrape_computrabajo(query, max_pages)
        for raw in raw_results:
            try:
                listings.append(JobListing(
                    title=raw.get("title", "Sin título"),
                    company=raw.get("company", "Empresa no especificada"),
                    location=raw.get("location"),
                    modality=raw.get("modality"),
                    description=raw.get("description", ""),
                    source_url=raw.get("url", ""),
                    source_platform="computrabajo",
                ))
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Error en scrape computrabajo: {e}")
    return listings

async def get_users_for_notifications(db: AsyncSession):
    """Obtiene usuarios con notificaciones activadas."""
    result = await db.execute(select(User).where(User.email_notifications_enabled == True))
    return result.scalars().all()

async def get_latest_analysis(db: AsyncSession, user_id: str):
    """Obtiene el análisis más reciente del usuario para extraer los job_titles."""
    result = await db.execute(
        select(CVAnalysis)
        .where(CVAnalysis.user_id == user_id)
        .order_by(CVAnalysis.created_at.desc())
        .limit(1)
    )
    return result.scalars().first()

def generate_email_html(user: User, job_listings: list, job_titles: list) -> str:
    """Genera el contenido HTML premium para el correo."""
    titles_str = ", ".join(job_titles)
    
    # Construir items de ofertas
    jobs_html = ""
    for job in job_listings[:10]:  # Limitar a las mejores 10 ofertas
        jobs_html += f"""
        <div style="background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <h3 style="margin: 0 0 8px 0; color: #111827; font-size: 18px;">{job.get('title', 'Posición no especificada')}</h3>
            <p style="margin: 0 0 8px 0; color: #4b5563; font-size: 14px;"><strong>Empresa:</strong> {job.get('company', 'No especificada')} | <strong>Ubicación:</strong> {job.get('location', 'No especificada')}</p>
            <p style="margin: 0 0 16px 0; color: #6b7280; font-size: 14px; line-height: 1.5;">{job.get('description', '')[:150]}...</p>
            <a href="{job.get('source_url', '#')}" style="display: inline-block; background-color: #2563eb; color: #ffffff; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; font-size: 14px;">Ver Oferta</a>
        </div>
        """

    if not job_listings:
        jobs_html = "<p style='color: #4b5563;'>No encontramos nuevas ofertas exactas esta semana, pero seguiremos buscando.</p>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="background-color: #1e3a8a; padding: 24px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Tus Recomendaciones de Empleo Semanales</h1>
            </div>
            <div style="padding: 24px;">
                <p style="color: #374151; font-size: 16px; line-height: 1.5;">Hola,</p>
                <p style="color: #374151; font-size: 16px; line-height: 1.5;">Aquí tienes las mejores ofertas laborales que encontramos esta semana basadas en tu perfil y tus búsquedas de: <strong>{titles_str}</strong>.</p>
                
                <div style="margin-top: 24px;">
                    {jobs_html}
                </div>
                
                <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 32px 0;">
                
                <p style="color: #9ca3af; font-size: 12px; text-align: center;">
                    Recibes este correo porque tienes las notificaciones activadas en CV Analyzer.<br>
                    Puedes desactivar estos correos desde tu perfil en la plataforma.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_email(to_email: str, subject: str, html_content: str):
    """Envía el correo usando SMTP."""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning(f"Credenciales SMTP no configuradas. Omitiendo correo a {to_email}")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg.set_content("Por favor, usa un cliente de correo que soporte HTML.")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Correo enviado exitosamente a {to_email}")
    except Exception as e:
        logger.error(f"Error enviando correo a {to_email}: {e}")

async def run_weekly_job_matcher():
    """Función principal del Cron Job."""
    logger.info("Iniciando Weekly Job Matcher Cron Job...")
    
    async with AsyncSessionLocal() as db:
        users = await get_users_for_notifications(db)
        logger.info(f"Se encontraron {len(users)} usuarios con notificaciones activadas.")
        
        for user in users:
            if not user.email:
                continue
                
            logger.info(f"Procesando usuario: {user.email}")
            latest_analysis = await get_latest_analysis(db, user.id)
            
            if not latest_analysis or not latest_analysis.job_titles:
                logger.info(f"Usuario {user.email} no tiene análisis previos o títulos. Saltando.")
                continue
                
            job_titles = latest_analysis.job_titles
            search_query = " OR ".join(job_titles)
            
            # Ejecutar scrapers silenciosa y asíncronamente
            all_jobs = []
            logger.info(f"Buscando '{search_query}' en LinkedIn...")
            all_jobs.extend(await search_jobs_linkedin_async(search_query))
            logger.info(f"Buscando '{search_query}' en Indeed...")
            all_jobs.extend(await search_jobs_indeed_async(search_query))
            logger.info(f"Buscando '{search_query}' en Computrabajo...")
            all_jobs.extend(await search_jobs_computrabajo_async(search_query))
            
            # Eliminar duplicados y vacíos
            unique_jobs = []
            seen_links = set()
            for job in all_jobs:
                if job.source_url and job.source_url not in seen_links:
                    seen_links.add(job.source_url)
                    unique_jobs.append(job)
                    
            logger.info(f"Se encontraron {len(unique_jobs)} ofertas únicas para {user.email}")
            
            # Generar y enviar correo (dump de los modelos a dicts para el generador HTML)
            jobs_dicts = [j.model_dump() for j in unique_jobs]
            html_content = generate_email_html(user, jobs_dicts, job_titles)
            subject = f"Nuevas Ofertas Laborales para ti: {', '.join(job_titles[:2])}"
            
            send_email(user.email, subject, html_content)
            
            # Pequeña pausa para no saturar el servidor SMTP
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_weekly_job_matcher())

