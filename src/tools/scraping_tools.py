"""
Herramientas de web scraping para obtener ofertas laborales.

Incluye:
    - search_jobs_computrabajo: Scraping de Computrabajo Argentina.
    - get_mock_job_listings: Datos de respaldo cuando el scraping falla.
"""

from __future__ import annotations

import asyncio
import random
import json

from loguru import logger

from src.config.settings import settings
from src.models.job_models import JobListing


async def _scrape_computrabajo(query: str, max_pages: int = 2) -> list[dict]:
    """
    Scrapea Computrabajo Argentina buscando ofertas laborales.

    Args:
        query: Término de búsqueda.
        max_pages: Máximo de páginas a scrapear.

    Returns:
        Lista de dicts con datos crudos de ofertas.
    """
    from playwright.async_api import async_playwright

    results = []
    search_url_base = "https://www.computrabajo.com.ar/trabajo-de-{query}"

    # Normalizar query para URL
    url_query = query.lower().replace(" ", "-")
    url = search_url_base.format(query=url_query)

    logger.info("Scrapeando Computrabajo: {}", url)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()

            for page_num in range(1, max_pages + 1):
                page_url = url if page_num == 1 else f"{url}?p={page_num}"

                try:
                    await page.goto(page_url, wait_until="domcontentloaded", timeout=15000)

                    # Esperar a que carguen las ofertas
                    await page.wait_for_selector(
                        "article.box_offer, div.box_offer, .iO",
                        timeout=8000,
                    )

                    # Extraer ofertas
                    listings = await page.evaluate("""
                        () => {
                            const items = document.querySelectorAll(
                                'article.box_offer, div.box_offer, .iO'
                            );
                            return Array.from(items).map(item => {
                                const titleEl = item.querySelector(
                                    'a.js-o-link, h2 a, .fc_base a'
                                );
                                const companyEl = item.querySelector(
                                    'a.fc_base, .fs16.fc_base, span.fc_base'
                                );
                                const descEl = item.querySelector(
                                    'p.fs13, .fs13'
                                );
                                return {
                                    title: titleEl ? titleEl.textContent.trim() : '',
                                    company: companyEl ? companyEl.textContent.trim() : '',
                                    description: descEl ? descEl.textContent.trim() : '',
                                    url: titleEl ? titleEl.href : '',
                                };
                            }).filter(item => item.title);
                        }
                    """)

                    for listing in listings:
                        listing["source_platform"] = "computrabajo"
                        results.append(listing)

                    logger.info(
                        "Página {}: {} ofertas encontradas", page_num, len(listings)
                    )

                except Exception as e:
                    logger.warning("Error en página {}: {}", page_num, e)

                # Delay aleatorio entre páginas
                if page_num < max_pages:
                    delay = random.uniform(
                        settings.scraping_delay_min,
                        settings.scraping_delay_max,
                    )
                    await asyncio.sleep(delay)

            await browser.close()

    except Exception as e:
        logger.error("Error general en scraping de Computrabajo: {}", e)

    return results


def search_jobs_computrabajo(query: str, max_pages: int = 2) -> list[JobListing]:
    """
    Wrapper síncrono para el scraping de Computrabajo.

    Args:
        query: Término de búsqueda.
        max_pages: Máximo de páginas a scrapear.

    Returns:
        Lista de JobListing parseados.
    """
    try:
        raw_results = asyncio.run(_scrape_computrabajo(query, max_pages))
    except RuntimeError:
        # Si ya hay un event loop corriendo (ej: en Streamlit), crear uno nuevo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            raw_results = loop.run_until_complete(
                _scrape_computrabajo(query, max_pages)
            )
        finally:
            loop.close()

    listings = []
    for raw in raw_results:
        try:
            listing = JobListing(
                title=raw.get("title", "Sin título"),
                company=raw.get("company", "Empresa no especificada"),
                location=raw.get("location"),
                modality=raw.get("modality"),
                description=raw.get("description", ""),
                source_url=raw.get("url", ""),
                source_platform="computrabajo",
            )
            listings.append(listing)
        except Exception as e:
            logger.debug("Error parseando listing: {}", e)

    logger.info(
        "Scraping completado: {} ofertas válidas de '{}'",
        len(listings),
        query,
    )
    return listings


def get_mock_job_listings(job_title: str = "Desarrollador Python") -> list[JobListing]:
    """
    Retorna datos de respaldo cuando el scraping falla.

    Útil para desarrollo, testing y demos en vivo.

    Args:
        job_title: Título base para generar las ofertas mock.

    Returns:
        Lista de JobListing de ejemplo.
    """
    logger.warning("Usando datos de respaldo (mock) para ofertas laborales")

    mock_data = [
        JobListing(
            title=f"{job_title} Semi-Senior",
            company="TechCorp Argentina",
            location="Buenos Aires, Argentina",
            modality="híbrido",
            description="Buscamos desarrollador Python con experiencia en Django/FastAPI, bases de datos SQL, y metodologías ágiles.",
            required_skills=["Python", "Django", "SQL", "Git", "API REST"],
            preferred_skills=["Docker", "AWS", "CI/CD", "Redis"],
            required_experience_years=3,
            salary_range="$800.000 - $1.200.000 ARS",
            source_url="https://example.com/job/1",
            source_platform="mock",
        ),
        JobListing(
            title=f"{job_title} Senior",
            company="DataSoft SRL",
            location="Córdoba, Argentina",
            modality="remoto",
            description="Se requiere desarrollador senior Python para equipo de datos. Machine Learning, ETL pipelines y cloud computing.",
            required_skills=["Python", "Machine Learning", "SQL", "Pandas", "AWS"],
            preferred_skills=["Spark", "Airflow", "Terraform", "Kubernetes"],
            required_experience_years=5,
            source_url="https://example.com/job/2",
            source_platform="mock",
        ),
        JobListing(
            title="Full Stack Developer",
            company="StartupXYZ",
            location="Remoto - Argentina",
            modality="remoto",
            description="Startup en crecimiento busca full stack developer. React + Python/Node.js. Experiencia en microservicios y bases de datos NoSQL.",
            required_skills=["Python", "JavaScript", "React", "Node.js", "MongoDB"],
            preferred_skills=["TypeScript", "GraphQL", "Docker", "CI/CD"],
            required_experience_years=2,
            salary_range="USD 2.000 - 3.500",
            source_url="https://example.com/job/3",
            source_platform="mock",
        ),
        JobListing(
            title="Data Engineer",
            company="FinanzasAI",
            location="Buenos Aires, Argentina",
            modality="híbrido",
            description="Buscamos data engineer para construir pipelines de datos. Experiencia en Python, SQL, cloud y herramientas ETL.",
            required_skills=["Python", "SQL", "ETL", "AWS", "Airflow"],
            preferred_skills=["Spark", "Kafka", "dbt", "Terraform"],
            required_experience_years=3,
            source_url="https://example.com/job/4",
            source_platform="mock",
        ),
        JobListing(
            title="Backend Developer Python",
            company="E-Commerce Plus",
            location="Rosario, Argentina",
            modality="presencial",
            description="Empresa de e-commerce busca backend developer. FastAPI, PostgreSQL, Redis, testing automatizado.",
            required_skills=["Python", "FastAPI", "PostgreSQL", "Redis", "Testing"],
            preferred_skills=["Docker", "Kubernetes", "RabbitMQ", "Elasticsearch"],
            required_experience_years=2,
            salary_range="$600.000 - $900.000 ARS",
            source_url="https://example.com/job/5",
            source_platform="mock",
        ),
        JobListing(
            title="DevOps / SRE Engineer",
            company="CloudNative SA",
            location="Buenos Aires, Argentina",
            modality="remoto",
            description="Buscamos DevOps/SRE con experiencia en infraestructura cloud, CI/CD, contenedores y automatización con Python.",
            required_skills=["Python", "Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
            preferred_skills=["Terraform", "Ansible", "Prometheus", "Go"],
            required_experience_years=4,
            source_url="https://example.com/job/6",
            source_platform="mock",
        ),
        JobListing(
            title="Machine Learning Engineer",
            company="AI Solutions",
            location="Remoto - LATAM",
            modality="remoto",
            description="Equipo de IA busca ML Engineer. Modelos de NLP, computer vision, deployment de modelos en producción.",
            required_skills=["Python", "Machine Learning", "TensorFlow", "PyTorch", "NLP"],
            preferred_skills=["MLOps", "Kubeflow", "FastAPI", "Docker"],
            required_experience_years=3,
            salary_range="USD 3.000 - 5.000",
            source_url="https://example.com/job/7",
            source_platform="mock",
        ),
        JobListing(
            title=f"{job_title} Junior",
            company="Software Factory AR",
            location="Buenos Aires, Argentina",
            modality="híbrido",
            description="Oportunidad para desarrolladores junior. Python, Git, SQL básico. Mentoring y capacitación incluida.",
            required_skills=["Python", "Git", "SQL"],
            preferred_skills=["Django", "HTML", "CSS", "JavaScript"],
            required_experience_years=1,
            salary_range="$400.000 - $600.000 ARS",
            source_url="https://example.com/job/8",
            source_platform="mock",
        ),
    ]

    return mock_data


async def _scrape_indeed(query: str, max_pages: int = 1) -> list[dict]:
    """
    Scrapea Indeed Argentina buscando ofertas laborales.
    """
    from playwright.async_api import async_playwright

    results = []
    # Indeed usa q=query
    url_query = query.replace(" ", "+")
    url = f"https://ar.indeed.com/jobs?q={url_query}"

    logger.info("Scrapeando Indeed: {}", url)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()

            for page_num in range(1, max_pages + 1):
                start = (page_num - 1) * 10
                page_url = url if page_num == 1 else f"{url}&start={start}"

                try:
                    await page.goto(page_url, wait_until="domcontentloaded", timeout=12000)

                    # Esperar por los contenedores de Indeed
                    await page.wait_for_selector(
                        "div.job_seen_beacon, td.resultContent, .jobCard_mainContent",
                        timeout=5000,
                    )

                    # Extraer ofertas
                    listings = await page.evaluate("""
                        () => {
                            const items = document.querySelectorAll(
                                'div.job_seen_beacon, td.resultContent'
                            );
                            return Array.from(items).map(item => {
                                const titleEl = item.querySelector(
                                    'h2.jobTitle a, h2.jobTitle span'
                                );
                                const companyEl = item.querySelector(
                                    '[data-testid="company-name"], .companyName'
                                );
                                const descEl = item.querySelector(
                                    '.job-snippet, .summary'
                                );
                                const urlEl = item.querySelector('h2.jobTitle a');
                                return {
                                    title: titleEl ? titleEl.textContent.trim() : '',
                                    company: companyEl ? companyEl.textContent.trim() : '',
                                    description: descEl ? descEl.textContent.trim() : '',
                                    url: urlEl ? urlEl.href : '',
                                };
                            }).filter(item => item.title);
                        }
                    """)

                    for listing in listings:
                        listing["source_platform"] = "indeed"
                        results.append(listing)

                    logger.info(
                        "Indeed Página {}: {} ofertas encontradas", page_num, len(listings)
                    )

                except Exception as e:
                    logger.warning("Error en Indeed página {}: {}", page_num, e)

                if page_num < max_pages:
                    await asyncio.sleep(random.uniform(1.5, 3.0))

            await browser.close()

    except Exception as e:
        logger.error("Error general en scraping de Indeed: {}", e)

    return results


def search_jobs_indeed(query: str, max_pages: int = 1) -> list[JobListing]:
    """
    Wrapper síncrono para el scraping de Indeed.
    """
    try:
        raw_results = asyncio.run(_scrape_indeed(query, max_pages))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            raw_results = loop.run_until_complete(
                _scrape_indeed(query, max_pages)
            )
        finally:
            loop.close()

    listings = []
    for raw in raw_results:
        try:
            listing = JobListing(
                title=raw.get("title", "Sin título"),
                company=raw.get("company", "Empresa no especificada"),
                location=raw.get("location"),
                modality=raw.get("modality"),
                description=raw.get("description", ""),
                source_url=raw.get("url", ""),
                source_platform="indeed",
            )
            listings.append(listing)
        except Exception as e:
            logger.debug("Error parseando Indeed listing: {}", e)

    logger.info(
        "Scraping Indeed completado: {} ofertas válidas de '{}'",
        len(listings),
        query,
    )
    return listings


async def _scrape_linkedin(query: str, max_pages: int = 1) -> list[dict]:
    """
    Scrapea LinkedIn público buscando ofertas laborales.
    """
    from playwright.async_api import async_playwright

    url_query = query.replace(" ", "%20")
    url = f"https://www.linkedin.com/jobs/search/?keywords={url_query}"

    logger.info("Scrapeando LinkedIn: {}", url)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=12000)

            # Esperar por el contenedor de ofertas de LinkedIn
            await page.wait_for_selector(
                ".jobs-search__results-list, li.jobs-search-card",
                timeout=5000,
            )

            listings = await page.evaluate("""
                () => {
                    const items = document.querySelectorAll(
                        '.jobs-search__results-list > li, li.jobs-search-card'
                    );
                    return Array.from(items).map(item => {
                        const titleEl = item.querySelector(
                            '.base-search-card__title, .job-search-card__title'
                        );
                        const companyEl = item.querySelector(
                            '.base-search-card__subtitle, .job-search-card__subtitle'
                        );
                        const urlEl = item.querySelector(
                            'a.base-card__full-link, a.job-search-card__link'
                        );
                        return {
                            title: titleEl ? titleEl.textContent.trim() : '',
                            company: companyEl ? companyEl.textContent.trim() : '',
                            description: 'Oferta de empleo en LinkedIn',
                            url: urlEl ? urlEl.href : '',
                        };
                    }).filter(item => item.title);
                }
            """)

            for listing in listings:
                listing["source_platform"] = "linkedin"

            await browser.close()
            return listings

    except Exception as e:
        logger.warning("No se pudo scrapear LinkedIn en vivo (esperado debido a políticas anti-bot): {}", e)
        return []


def search_jobs_linkedin(query: str, max_pages: int = 1) -> list[JobListing]:
    """
    Wrapper síncrono para el scraping de LinkedIn.
    """
    try:
        raw_results = asyncio.run(_scrape_linkedin(query, max_pages))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            raw_results = loop.run_until_complete(
                _scrape_linkedin(query, max_pages)
            )
        finally:
            loop.close()

    listings = []
    for raw in raw_results:
        try:
            listing = JobListing(
                title=raw.get("title", "Sin título"),
                company=raw.get("company", "Empresa no especificada"),
                location=raw.get("location"),
                modality=raw.get("modality"),
                description=raw.get("description", ""),
                source_url=raw.get("url", ""),
                source_platform="linkedin",
            )
            listings.append(listing)
        except Exception as e:
            logger.debug("Error parseando LinkedIn listing: {}", e)

    logger.info(
        "Scraping LinkedIn completado: {} ofertas válidas de '{}'",
        len(listings),
        query,
    )
    return listings


async def _scrape_bumeran(query: str, max_pages: int = 1) -> list[dict]:
    """
    Scrapea Bumeran Argentina buscando ofertas laborales.
    """
    from playwright.async_api import async_playwright

    url_query = query.lower().replace(" ", "-")
    url = f"https://www.bumeran.com.ar/empleos-busqueda-{url_query}.html"

    logger.info("Scrapeando Bumeran: {}", url)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=12000)

            # Esperar por los contenedores de Bumeran
            await page.wait_for_selector(
                "div[class*='JobCard'], div[class*='CardContainer'], a[class*='JobCard']",
                timeout=5000,
            )

            listings = await page.evaluate("""
                () => {
                    const items = document.querySelectorAll(
                        'div[class*="CardContainer"], a[class*="JobCard"], div[class*="JobCard"]'
                    );
                    return Array.from(items).map(item => {
                        const titleEl = item.querySelector('h2, [class*="Title"], [class*="title"]');
                        const companyEl = item.querySelector('[class*="Company"], [class*="Employer"], [class*="employer"]');
                        const urlEl = item.tagName === 'A' ? item : item.querySelector('a');
                        return {
                            title: titleEl ? titleEl.textContent.trim() : '',
                            company: companyEl ? companyEl.textContent.trim() : '',
                            description: 'Oferta de empleo en Bumeran',
                            url: urlEl ? urlEl.href : '',
                        };
                    }).filter(item => item.title);
                }
            """)

            for listing in listings:
                listing["source_platform"] = "bumeran"

            await browser.close()
            return listings

    except Exception as e:
        logger.warning("No se pudo scrapear Bumeran en vivo: {}", e)
        return []


def search_jobs_bumeran(query: str, max_pages: int = 1) -> list[JobListing]:
    """
    Wrapper síncrono para el scraping de Bumeran.
    """
    try:
        raw_results = asyncio.run(_scrape_bumeran(query, max_pages))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            raw_results = loop.run_until_complete(
                _scrape_bumeran(query, max_pages)
            )
        finally:
            loop.close()

    listings = []
    for raw in raw_results:
        try:
            listing = JobListing(
                title=raw.get("title", "Sin título"),
                company=raw.get("company", "Empresa no especificada"),
                location=raw.get("location"),
                modality=raw.get("modality"),
                description=raw.get("description", ""),
                source_url=raw.get("url", ""),
                source_platform="bumeran",
            )
            listings.append(listing)
        except Exception as e:
            logger.debug("Error parseando Bumeran listing: {}", e)

    logger.info(
        "Scraping Bumeran completado: {} ofertas válidas de '{}'",
        len(listings),
        query,
    )
    return listings


