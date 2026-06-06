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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton de configuración
settings = Settings()
