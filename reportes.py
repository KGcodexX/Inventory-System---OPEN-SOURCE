"""Generacion de reportes de Economia en PDF (corte de caja)."""
import os
from datetime import datetime

from fpdf import FPDF

REPORTES_DIR = "reportes"


def _tabla(pdf, titulo, columnas, anchos, filas):
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, titulo, new_x="LMARGIN", new_y="NEXT")

    if not filas:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Sin datos", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        return

    pdf.set_font("Helvetica", "B", 10)
    for col, ancho in zip(columnas, anchos):
        pdf.cell(ancho, 7, col, border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    for fila in filas:
        for valor, ancho in zip(fila, anchos):
            pdf.cell(ancho, 7, str(valor), border=1)
        pdf.ln()
    pdf.ln(3)


def generar_reporte_economia_pdf(resumen):
    os.makedirs(REPORTES_DIR, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte de Economia", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(0, 8, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Total hoy: ${resumen['total_hoy']:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Total mes: ${resumen['total_mes']:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Ganancia hoy: ${resumen['ganancia_hoy']:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Ganancia mes: ${resumen['ganancia_mes']:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Ventas hoy: {resumen['ventas_hoy']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Ventas mes: {resumen['ventas_mes']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    _tabla(pdf, "Top perfumes (por cantidad)", ("Perfume", "Cantidad"), (100, 50), resumen["top_cantidad"])
    _tabla(pdf, "Top perfumes (por dinero)", ("Perfume", "Total"), (100, 50), resumen["top_dinero"])
    _tabla(pdf, "Top clientes", ("Cliente", "Total"), (100, 50), resumen["top_clientes"])
    _tabla(pdf, "Menos vendidos", ("Perfume", "Cantidad"), (100, 50), resumen["menos_vendidos"])
    _tabla(pdf, "Stock bajo", ("Marca", "Perfume", "Existencias"), (60, 70, 40), resumen["stock_bajo"])
    _tabla(
        pdf, "Prediccion de agotamiento", ("Perfume", "Existencias", "Dias restantes"),
        (70, 50, 50), resumen["dias_restantes"]
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join(REPORTES_DIR, f"reporte_economia_{timestamp}.pdf")
    pdf.output(ruta)
    return ruta
