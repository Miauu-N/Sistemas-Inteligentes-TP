# Usar la imagen oficial de Microsoft Playwright para Python.
# Esta imagen ya viene con Python, Chromium y todas las dependencias de Linux preinstaladas.
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiar archivo de requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente del proyecto
COPY . .

# Exponer el puerto (Render lo sobreescribirá con la variable $PORT)
EXPOSE 8000

# Comando de inicio del servidor
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
