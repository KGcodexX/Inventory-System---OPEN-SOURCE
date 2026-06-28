"""Generacion de recibos de venta en PDF."""
import os
from datetime import datetime

from fpdf import FPDF

from db import cursor

RECIBOS_DIR = "recibos"


def generar_recibo_pdf(venta_id):
    cursor.execute("""
        SELECT v.id, v.fecha, v.metodo_pago, c.nombre
        FROM ventas v
        JOIN clientes c ON v.cliente_id = c.id
        WHERE v.id = ?
    """, (venta_id,))
    venta = cursor.fetchone()
    if venta is None:
        return None

    _, fecha, metodo_pago, cliente_nombre = venta

    cursor.execute("""
        SELECT d.nombre_perfume, COALESCE(i.marca, ''), d.cantidad, d.tipo_precio, d.total
        FROM detalle_venta d
        LEFT JOIN inventario i ON d.perfume_id = i.id
        WHERE d.venta_id = ?
    """, (venta_id,))
    items = cursor.fetchall()

    total_venta = sum(item[4] for item in items)

    os.makedirs(RECIBOS_DIR, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Recibo de venta", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.ln(4)
    pdf.cell(0, 8, f"Venta #{venta_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Fecha: {fecha}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Cliente: {cliente_nombre}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Metodo de pago: {metodo_pago}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(50, 8, "Perfume", border=1)
    pdf.cell(35, 8, "Marca", border=1)
    pdf.cell(25, 8, "Cantidad", border=1, align="C")
    pdf.cell(35, 8, "Tipo precio", border=1, align="C")
    pdf.cell(35, 8, "Total", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    for nombre_perfume, marca, cantidad, tipo_precio, total in items:
        pdf.cell(50, 8, str(nombre_perfume), border=1)
        pdf.cell(35, 8, str(marca), border=1)
        pdf.cell(25, 8, str(cantidad), border=1, align="C")
        pdf.cell(35, 8, str(tipo_precio), border=1, align="C")
        pdf.cell(35, 8, f"${total:.2f}", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Total: ${total_venta:.2f}", align="R")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join(RECIBOS_DIR, f"recibo_venta_{venta_id}_{timestamp}.pdf")
    pdf.output(ruta)
    return ruta
