# 🎨 CV Analyzer — Frontend

Esta carpeta contiene el cliente web SPA desarrollado en **React 19** utilizando **Vite** como empaquetador y **Tailwind CSS v4** para el diseño de interfaces. La UI cuenta con un diseño premium *Glassmorphism* (traslúcido y dinámico) y consume el backend asíncrono en tiempo real.

---

## 🛠️ Stack Tecnológico

*   **Core:** React 19 (Hooks, Context y HOCs)
*   **Empaquetador/Servidor Dev:** Vite 8
*   **Identidad y Autenticación:** SDK Oficial de `@auth0/auth0-react`
*   **Estilos:** Tailwind CSS v4 (Vanilla CSS sin dependencias heredadas de configuración)
*   **Iconografía:** Lucide React

---

## 🚀 Instalación y Desarrollo Local

### 1. Requisitos
*   Node.js (v18 o superior)
*   npm (v9 o superior)

### 2. Configuración
1. Instala las dependencias del proyecto:
   ```bash
   npm install
   ```

2. Configura las variables de entorno locales:
   Crea un archivo `.env` dentro de la carpeta `frontend/` con las siguientes credenciales:
   ```env
   # URL del servidor backend de FastAPI
   VITE_API_URL=http://localhost:8000

   # Configuración de tu aplicación en Auth0 (Consola de Auth0)
   VITE_AUTH0_DOMAIN=dev-e8l3n5ui627xcocw.us.auth0.com
   VITE_AUTH0_CLIENT_ID=f2nsCqndLy8vnhz7weGlzEPE5ATHqhZ4
   VITE_AUTH0_AUDIENCE=cv-analyzer-api
   ```

### 3. Ejecutar en Desarrollo
Inicia el servidor local de desarrollo de Vite:
```bash
npm run dev
```
La aplicación se abrirá automáticamente en **`http://localhost:5173/`**.

---

## 📂 Estructura de Componentes Clave

*   **`main.jsx`:** Punto de entrada donde se inicializa React y se envuelve la aplicación en el `<Auth0Provider>` para inyectar el estado de autenticación de manera global.
*   **`App.jsx`:** Orquestador principal de la app.
    *   Gestiona los estados globales del análisis (`idle`, `uploading`, `analyzing`, `completed`, `error`).
    *   Controla el flujo de redirecciones si el usuario no ha iniciado sesión.
    *   Consume los eventos en tiempo real enviados por el backend (SSE) para actualizar la barra de progreso.
*   **`components/UploadSection.jsx`:** Área drag-and-drop para arrastrar currículums en PDF con selector premium para elegir el motor de búsqueda (Scraping Web con checkboxes de portales vs SerpAPI/Google Jobs).
*   **`components/ProgressTracker.jsx`:** Barra de progreso fluida que muestra el paso actual de la IA.
*   **`components/Dashboard.jsx`:** Layout interactivo estilo *bento-grid* para ver las métricas de alineación, fortalezas, brechas, plan de acción interactivo (con checkboxes que persisten el estado completado en la base de datos) y vacantes recomendadas (con dos botones ágiles de re-escaneo: Scraping y SerpAPI).
*   **`components/ProfileSettings.jsx`:** Panel de cuenta de usuario donde se muestra la sesión activa de Auth0 y el interruptor (Toggle) para habilitar/deshabilitar los boletines semanales de empleo.

---

## ☁️ Despliegue en Producción (Vercel)

El frontend está optimizado para desplegarse fácilmente en **Vercel** o plataformas estáticas equivalentes:

1. En Vercel, crea un nuevo proyecto e importa el repositorio general.
2. En la configuración del proyecto, define la carpeta **`frontend`** como el **Root Directory**.
3. Asegúrate de inyectar las 4 variables de entorno (`VITE_API_URL` apuntando a tu backend de Render, y las tres variables `VITE_AUTH0_*`).
4. En tu panel de Auth0, recuerda agregar la URL de producción que te dé Vercel dentro de las listas blancas de **Application URIs**:
   *   *Allowed Callback URLs*
   *   *Allowed Logout URLs*
   *   *Allowed Web Origins*
