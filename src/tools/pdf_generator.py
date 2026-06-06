import json
from fpdf import FPDF

class CVReportPDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 18)
        # Título
        self.cell(0, 10, 'CV Analyzer - Reporte de Empleabilidad', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Análisis Inteligente y Recomendaciones', 0, 1, 'C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        # Posición a 1.5 cm del final
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        # Número de página
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.set_text_color(0)
        # Usar utf-8 decoder para caracteres especiales
        text = str(text).encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, text)
        self.ln(5)
        
    def add_bullet(self, text):
        self.set_font('Arial', '', 11)
        self.set_text_color(0)
        text = str(text).encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, f"- {text}")
        self.ln(2)

def generate_pdf_report(report_data: dict, filepath: str):
    """
    Genera un PDF con el informe de empleabilidad usando FPDF2.
    """
    pdf = CVReportPDF()
    pdf.add_page()
    
    cv_summary = report_data.get("cv_summary", {})
    matching_score = report_data.get("matching_score", 0.0)
    executive_summary = report_data.get("executive_summary", "Sin resumen.")
    
    # Perfil
    pdf.chapter_title("1. Perfil del Candidato")
    name = cv_summary.get("name", "Desconocido")
    seniority = cv_summary.get("seniority", "No determinado")
    pdf.chapter_body(f"Nombre: {name}\nSeniority: {seniority}")
    
    # Resumen Ejecutivo
    pdf.chapter_title("2. Resumen Ejecutivo")
    pdf.chapter_body(executive_summary)
    
    # Score
    pdf.chapter_title("3. Alineación con el Mercado")
    pdf.chapter_body(f"Score de coincidencia: {int(matching_score * 100)}%")
    
    # Fortalezas
    strengths = report_data.get("strengths", [])
    if strengths:
        pdf.chapter_title("4. Fortalezas Detectadas")
        for s in strengths:
            pdf.add_bullet(s)
        pdf.ln(5)
            
    # Brechas
    gaps = report_data.get("gaps", [])
    if gaps:
        pdf.chapter_title("5. Brechas Identificadas")
        for gap in gaps:
            desc = gap.get("description", "")
            pdf.add_bullet(f"{gap.get('skill_or_requirement', '')}: {desc}")
        pdf.ln(5)
            
    # Recomendaciones
    recs = report_data.get("recommendations", [])
    if recs:
        pdf.chapter_title("6. Recomendaciones")
        for i, rec in enumerate(recs, 1):
            title = rec.get("title", "")
            desc = rec.get("description", "")
            time = rec.get("estimated_time", "")
            
            # Limpiar caracteres conflictivos
            title = title.encode('latin-1', 'replace').decode('latin-1')
            desc = desc.encode('latin-1', 'replace').decode('latin-1')
            time = time.encode('latin-1', 'replace').decode('latin-1')
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 6, f"{i}. {title} ({time})", 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 6, desc)
            pdf.ln(3)

    pdf.output(filepath)
    return filepath
