"""
Configuración centralizada del proyecto.
Carga variables de entorno desde .env y las expone como atributos tipados.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuración global de la aplicación."""

    # --- Google Gemini ---
    google_api_key: str = Field(
        default="",
        description="API Key de Google Gemini"
    )
    gemini_model: str = Field(
        default="gemini-3.1-flash-lite",
        description="Modelo de Gemini a utilizar"
    )

    # --- Scraping ---
    max_search_pages: int = Field(
        default=3,
        description="Máximo de páginas a scrapear por portal"
    )
    scraping_delay_min: int = Field(
        default=2,
        description="Delay mínimo entre requests de scraping (segundos)"
    )
    scraping_delay_max: int = Field(
        default=5,
        description="Delay máximo entre requests de scraping (segundos)"
    )

    # --- PDF ---
    max_pdf_size_mb: int = Field(
        default=10,
        description="Tamaño máximo del PDF en MB"
    )
    max_pdf_pages: int = Field(
        default=20,
        description="Número máximo de páginas del PDF"
    )

    # --- General ---
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging"
    )

    # --- NUEVOS PARÁMETROS FASE 6 ---
    database_url: str = Field(
        default="sqlite+aiosqlite:///./cv_analyzer.db",
        description="URL de conexión a la base de datos"
    )
    auth0_domain: str = Field(
        default="dev-e8l3n5ui627xcocw.us.auth0.com",
        description="Dominio de Auth0"
    )
    auth0_audience: str = Field(
        default="cv-analyzer-api",
        description="Audience de Auth0"
    )
    smtp_server: str = Field(
        default="smtp.gmail.com",
        description="Servidor SMTP"
    )
    smtp_port: int = Field(
        default=587,
        description="Puerto SMTP"
    )
    smtp_username: str = Field(
        default="",
        description="Usuario SMTP"
    )
    smtp_password: str = Field(
        default="",
        description="Contraseña SMTP"
    )
    sender_email: str = Field(
        default="",
        description="Remitente de correos"
    )

    # --- Proxy Configuration for Scraping ---
    proxy_server: str = Field(
        default="",
        description="URL del servidor proxy (ej: http://myproxy:8080)"
    )
    proxy_username: str = Field(
        default="",
        description="Usuario del proxy"
    )
    proxy_password: str = Field(
        default="",
        description="Contraseña del proxy"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignorar extras para evitar ValidationErrors por otras variables de entorno locales
    }


# Singleton de configuración
settings = Settings()
