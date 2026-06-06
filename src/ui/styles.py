"""
Estilos CSS personalizados para la aplicación Streamlit.
"""

CUSTOM_CSS = """
<style>
    /* --- Fuente y base --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* --- Header principal --- */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .main-header p {
        color: #6b7280;
        font-size: 1.1rem;
    }

    /* --- Cards --- */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
    }

    .metric-card .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.25rem;
    }

    .metric-card .metric-label {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* --- Score gauge --- */
    .score-container {
        text-align: center;
        padding: 2rem;
    }

    .score-high {
        color: #10b981;
    }

    .score-medium {
        color: #f59e0b;
    }

    .score-low {
        color: #ef4444;
    }

    .score-value {
        font-size: 4rem;
        font-weight: 700;
        line-height: 1;
    }

    .score-label {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 0.5rem;
    }

    /* --- Skill tags --- */
    .skill-tag {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.2rem;
    }

    .skill-tag-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }

    .skill-tag-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }

    .skill-tag-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }

    /* --- Gap cards --- */
    .gap-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .gap-card.priority-alta {
        border-left-color: #ef4444;
    }

    .gap-card.priority-media {
        border-left-color: #f59e0b;
    }

    .gap-card.priority-baja {
        border-left-color: #10b981;
    }

    /* --- Recommendation cards --- */
    .rec-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .rec-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }

    .rec-type-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-curso { background: #dbeafe; color: #1d4ed8; }
    .badge-certificación { background: #fef3c7; color: #92400e; }
    .badge-proyecto_práctico { background: #d1fae5; color: #065f46; }
    .badge-desarrollo_habilidad { background: #ede9fe; color: #5b21b6; }
    .badge-mejora_cv { background: #fce7f3; color: #9d174d; }
    .badge-networking { background: #e0e7ff; color: #3730a3; }

    /* --- Progress bar --- */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
    }

    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }

    .step-circle {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.85rem;
    }

    .step-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .step-completed {
        background: #10b981;
        color: white;
    }

    .step-pending {
        background: #e5e7eb;
        color: #9ca3af;
    }

    .step-label {
        font-size: 0.7rem;
        color: #6b7280;
        margin-top: 0.4rem;
        text-align: center;
    }

    /* --- Dividers --- */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #d1d5db, transparent);
        margin: 2rem 0;
    }

    /* --- Upload area --- */
    .upload-area {
        border: 2px dashed #d1d5db;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: #fafbfc;
        transition: border-color 0.3s ease;
    }

    .upload-area:hover {
        border-color: #667eea;
    }

    /* --- Executive summary --- */
    .executive-summary {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
        border-radius: 16px;
        padding: 2rem;
        line-height: 1.8;
        font-size: 1rem;
        color: #374151;
        border: 1px solid #e5e7eb;
    }

    /* --- Hide Streamlit branding --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
