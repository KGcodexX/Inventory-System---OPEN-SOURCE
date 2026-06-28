"""Ventana de resumen economico (ventas, ganancias, rankings)."""
import tkinter as tk
from tkinter import ttk

from config import BG_COLOR
from db import cursor


def abrir_economia():
    v = tk.Toplevel()
    v.title("Economía")
    v.configure(bg=BG_COLOR)
    v.geometry("900x600")
    v.minsize(850, 520)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
    v.grid_rowconfigure(0, weight=1)
    v.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # TOTAL HOY
    cursor.execute("""
        SELECT IFNULL(SUM(d.total),0)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE DATE(v.fecha)=DATE('now')
        AND v.metodo_pago!='Regalo'
    """)
    total_hoy = cursor.fetchone()[0]

    # TOTAL MES
    cursor.execute("""
        SELECT IFNULL(SUM(d.total),0)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE strftime('%m', v.fecha)=strftime('%m', 'now')
        AND strftime('%Y', v.fecha)=strftime('%Y', 'now')
        AND v.metodo_pago!='Regalo'
    """)
    total_mes = cursor.fetchone()[0]

    # GANANCIA HOY
    cursor.execute("""
        SELECT IFNULL(SUM(d.ganancia),0)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE DATE(v.fecha)=DATE('now')
        AND v.metodo_pago!='Regalo'
    """)
    ganancia_hoy = cursor.fetchone()[0]

    # GANANCIA MES
    cursor.execute("""
        SELECT IFNULL(SUM(d.ganancia),0)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE strftime('%m', v.fecha)=strftime('%m', 'now')
        AND strftime('%Y', v.fecha)=strftime('%Y', 'now')
        AND v.metodo_pago!='Regalo'
    """)
    ganancia_mes = cursor.fetchone()[0]

    # NUMERO DE VENTAS HOY
    cursor.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha)=DATE('now')")
    ventas_hoy = cursor.fetchone()[0]

    # NUMERO DE VENTAS MES
    cursor.execute("""
        SELECT COUNT(*) FROM ventas
        WHERE strftime('%m', fecha)=strftime('%m', 'now')
        AND strftime('%Y', fecha)=strftime('%Y', 'now')
    """)
    ventas_mes = cursor.fetchone()[0]

    # MOSTRAR RESUMEN
    tk.Label(frame, text="RESUMEN ECONOMICO", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
    tk.Label(frame, text=f"Total hoy: ${total_hoy}").grid(row=1, column=0, sticky="w")
    tk.Label(frame, text=f"Total mes: ${total_mes}").grid(row=2, column=0, sticky="w")
    tk.Label(frame, text=f"Ganancia hoy: ${ganancia_hoy}").grid(row=3, column=0, sticky="w")
    tk.Label(frame, text=f"Ganancia mes: ${ganancia_mes}").grid(row=4, column=0, sticky="w")
    tk.Label(frame, text=f"Ventas hoy: {ventas_hoy}").grid(row=5, column=0, sticky="w")
    tk.Label(frame, text=f"Ventas mes: {ventas_mes}").grid(row=6, column=0, sticky="w", pady=(0, 6))

    # ---------------- TOP PERFUMES CANTIDAD ----------------
    tk.Label(frame, text="Top perfumes (por cantidad)", font=("Arial", 12, "bold")).grid(row=7, column=0, sticky="w", pady=(6, 2))
    tabla1 = ttk.Treeview(frame, columns=("Perfume", "Cantidad"), show="headings", height=5)
    tabla1.heading("Perfume", text="Perfume")
    tabla1.heading("Cantidad", text="Cantidad")
    tabla1.grid(row=8, column=0, sticky="nsew")

    cursor.execute("""
        SELECT d.nombre_perfume, SUM(d.cantidad)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE v.metodo_pago!='Regalo'
        GROUP BY d.nombre_perfume
        ORDER BY SUM(d.cantidad) DESC
        LIMIT 5
    """)
    for fila in cursor.fetchall():
        tabla1.insert("", "end", values=fila)

    # ---------------- TOP PERFUMES DINERO ----------------
    tk.Label(frame, text="Top perfumes (por dinero)", font=("Arial", 12, "bold")).grid(row=9, column=0, sticky="w", pady=(6, 2))
    tabla2 = ttk.Treeview(frame, columns=("Perfume", "Total"), show="headings", height=5)
    tabla2.heading("Perfume", text="Perfume")
    tabla2.heading("Total", text="Total $")
    tabla2.grid(row=10, column=0, sticky="nsew")

    cursor.execute("""
        SELECT d.nombre_perfume, SUM(d.total)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE v.metodo_pago!='Regalo'
        GROUP BY d.nombre_perfume
        ORDER BY SUM(d.total) DESC
        LIMIT 5
    """)
    for fila in cursor.fetchall():
        tabla2.insert("", "end", values=fila)

    # ---------------- TOP CLIENTES ----------------
    tk.Label(frame, text="Top clientes", font=("Arial", 12, "bold")).grid(row=11, column=0, sticky="w", pady=(6, 2))
    tabla3 = ttk.Treeview(frame, columns=("Cliente", "Total"), show="headings", height=5)
    tabla3.heading("Cliente", text="Cliente")
    tabla3.heading("Total", text="Total $")
    tabla3.grid(row=12, column=0, sticky="nsew")

    cursor.execute("""
        SELECT c.nombre, SUM(d.total)
        FROM ventas v
        JOIN clientes c ON v.cliente_id=c.id
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE v.metodo_pago!='Regalo'
        GROUP BY c.nombre
        ORDER BY SUM(d.total) DESC
        LIMIT 5
    """)
    for fila in cursor.fetchall():
        tabla3.insert("", "end", values=fila)

    # ---------------- MENOS VENDIDOS ----------------
    tk.Label(frame, text="Menos vendidos", font=("Arial", 12, "bold")).grid(row=13, column=0, sticky="w", pady=(6, 2))
    tabla4 = ttk.Treeview(frame, columns=("Perfume", "Cantidad"), show="headings", height=5)
    tabla4.heading("Perfume", text="Perfume")
    tabla4.heading("Cantidad", text="Cantidad")
    tabla4.grid(row=14, column=0, sticky="nsew")

    cursor.execute("""
    SELECT d.nombre_perfume, SUM(d.cantidad)
    FROM ventas v
    JOIN detalle_venta d ON v.id = d.venta_id
    WHERE v.metodo_pago != 'Regalo'
    GROUP BY d.nombre_perfume
    ORDER BY SUM(d.cantidad) ASC
    LIMIT 5
    """)
    for fila in cursor.fetchall():
        tabla4.insert("", "end", values=fila)

    for r in (8, 10, 12, 14):
        frame.grid_rowconfigure(r, weight=1)
