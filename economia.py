"""Ventana de resumen economico (ventas, ganancias, rankings, stock bajo y prediccion de agotamiento)."""
import os
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import ACCENT_COLOR, BG_COLOR, CARD_BG, DIAS_VELOCIDAD_VENTA, TEXT_COLOR, UMBRAL_STOCK_BAJO
from db import cursor
from widgets import boton


def obtener_resumen():
    cursor.execute("""
        SELECT IFNULL(SUM(d.total),0)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE DATE(v.fecha)=DATE('now')
        AND v.metodo_pago!='Regalo'
    """)
    total_hoy = cursor.fetchone()[0]

    cursor.execute("""
        SELECT IFNULL(SUM(d.total),0)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE strftime('%m', v.fecha)=strftime('%m', 'now')
        AND strftime('%Y', v.fecha)=strftime('%Y', 'now')
        AND v.metodo_pago!='Regalo'
    """)
    total_mes = cursor.fetchone()[0]

    cursor.execute("""
        SELECT IFNULL(SUM(d.ganancia),0)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE DATE(v.fecha)=DATE('now')
        AND v.metodo_pago!='Regalo'
    """)
    ganancia_hoy = cursor.fetchone()[0]

    cursor.execute("""
        SELECT IFNULL(SUM(d.ganancia),0)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE strftime('%m', v.fecha)=strftime('%m', 'now')
        AND strftime('%Y', v.fecha)=strftime('%Y', 'now')
        AND v.metodo_pago!='Regalo'
    """)
    ganancia_mes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha)=DATE('now')")
    ventas_hoy = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM ventas
        WHERE strftime('%m', fecha)=strftime('%m', 'now')
        AND strftime('%Y', fecha)=strftime('%Y', 'now')
    """)
    ventas_mes = cursor.fetchone()[0]

    cursor.execute("""
        SELECT d.nombre_perfume, SUM(d.cantidad)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE v.metodo_pago!='Regalo'
        GROUP BY d.nombre_perfume
        ORDER BY SUM(d.cantidad) DESC
        LIMIT 5
    """)
    top_cantidad = cursor.fetchall()

    cursor.execute("""
        SELECT d.nombre_perfume, SUM(d.total)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE v.metodo_pago!='Regalo'
        GROUP BY d.nombre_perfume
        ORDER BY SUM(d.total) DESC
        LIMIT 5
    """)
    top_dinero = cursor.fetchall()

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
    top_clientes = cursor.fetchall()

    cursor.execute("""
        SELECT d.nombre_perfume, SUM(d.cantidad)
        FROM ventas v
        JOIN detalle_venta d ON v.id = d.venta_id
        WHERE v.metodo_pago != 'Regalo'
        GROUP BY d.nombre_perfume
        ORDER BY SUM(d.cantidad) ASC
        LIMIT 5
    """)
    menos_vendidos = cursor.fetchall()

    cursor.execute("""
        SELECT marca, nombre, existencias
        FROM inventario
        WHERE existencias <= ?
        ORDER BY existencias ASC
    """, (UMBRAL_STOCK_BAJO,))
    stock_bajo = cursor.fetchall()

    dias_restantes = _calcular_dias_restantes()

    return {
        "total_hoy": total_hoy,
        "total_mes": total_mes,
        "ganancia_hoy": ganancia_hoy,
        "ganancia_mes": ganancia_mes,
        "ventas_hoy": ventas_hoy,
        "ventas_mes": ventas_mes,
        "top_cantidad": top_cantidad,
        "top_dinero": top_dinero,
        "top_clientes": top_clientes,
        "menos_vendidos": menos_vendidos,
        "stock_bajo": stock_bajo,
        "dias_restantes": dias_restantes,
    }


def _calcular_dias_restantes():
    """Estima cuantos dias faltan para que se agote cada perfume, segun su
    velocidad de venta promedio en los ultimos DIAS_VELOCIDAD_VENTA dias."""
    cursor.execute("""
        SELECT i.nombre, i.existencias, COALESCE(SUM(d.cantidad), 0)
        FROM inventario i
        LEFT JOIN detalle_venta d ON d.perfume_id = i.id
        LEFT JOIN ventas v ON v.id = d.venta_id
            AND v.fecha >= datetime('now', ?)
            AND v.metodo_pago != 'Regalo'
        GROUP BY i.id
    """, (f"-{DIAS_VELOCIDAD_VENTA} days",))

    resultado = []
    for nombre, existencias, vendido in cursor.fetchall():
        velocidad_diaria = vendido / DIAS_VELOCIDAD_VENTA
        if velocidad_diaria <= 0:
            continue
        dias_restantes = existencias / velocidad_diaria
        resultado.append((nombre, existencias, round(dias_restantes, 1)))

    resultado.sort(key=lambda fila: fila[2])
    return resultado[:8]


def _llenar_tabla(frame, fila, titulo, columnas, datos, anchos=None):
    tk.Label(frame, text=titulo, font=("Arial", 12, "bold")).grid(row=fila, column=0, sticky="w", pady=(6, 2))
    tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=5)
    for i, col in enumerate(columnas):
        tabla.heading(col, text=col)
        tabla.column(col, width=(anchos[i] if anchos else 140))
    tabla.grid(row=fila + 1, column=0, sticky="nsew")
    for dato in datos:
        tabla.insert("", "end", values=dato)
    return fila + 2


def _grafica_top_perfumes(frame, fila, datos):
    tk.Label(frame, text="Grafica: top perfumes por dinero", font=("Arial", 12, "bold")).grid(
        row=fila, column=0, columnspan=2, sticky="w", pady=(10, 4))

    if not datos:
        return fila + 1

    nombres = [d[0] for d in datos]
    valores = [d[1] for d in datos]

    fig = Figure(figsize=(6.5, 3), dpi=100, facecolor=CARD_BG)
    ax = fig.add_subplot(111)
    ax.bar(nombres, valores, color=ACCENT_COLOR)
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax.set_ylabel("Total $", color=TEXT_COLOR, fontsize=9)
    for spine in ax.spines.values():
        spine.set_color(TEXT_COLOR)
    for etiqueta in ax.get_xticklabels():
        etiqueta.set_rotation(20)
        etiqueta.set_ha("right")
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().grid(row=fila + 1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

    return fila + 2


def exportar_reporte_economia():
    from reportes import generar_reporte_economia_pdf

    resumen = obtener_resumen()
    ruta = generar_reporte_economia_pdf(resumen)

    messagebox.showinfo("Reporte generado", f"Reporte guardado en:\n{os.path.abspath(ruta)}")
    try:
        os.startfile(ruta)
    except Exception:
        pass


def abrir_economia():
    v = tk.Toplevel()
    v.title("Economía")
    v.configure(bg=BG_COLOR)
    v.geometry("950x650")
    v.minsize(850, 520)

    canvas = tk.Canvas(v, bg=BG_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(v, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg=BG_COLOR)

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _activar_scroll(_event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _desactivar_scroll(_event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _activar_scroll)
    canvas.bind("<Leave>", _desactivar_scroll)
    v.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

    frame.grid_columnconfigure(0, weight=1)

    resumen = obtener_resumen()

    tk.Label(frame, text="RESUMEN ECONOMICO", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
    boton(frame, "Exportar reporte PDF", exportar_reporte_economia, width=20).grid(row=0, column=1, sticky="e", padx=(20, 0))

    tk.Label(frame, text=f"Total hoy: ${resumen['total_hoy']}").grid(row=1, column=0, sticky="w")
    tk.Label(frame, text=f"Total mes: ${resumen['total_mes']}").grid(row=2, column=0, sticky="w")
    tk.Label(frame, text=f"Ganancia hoy: ${resumen['ganancia_hoy']}").grid(row=3, column=0, sticky="w")
    tk.Label(frame, text=f"Ganancia mes: ${resumen['ganancia_mes']}").grid(row=4, column=0, sticky="w")
    tk.Label(frame, text=f"Ventas hoy: {resumen['ventas_hoy']}").grid(row=5, column=0, sticky="w")
    tk.Label(frame, text=f"Ventas mes: {resumen['ventas_mes']}").grid(row=6, column=0, sticky="w", pady=(0, 6))

    fila = 7
    fila = _grafica_top_perfumes(frame, fila, resumen["top_dinero"])
    fila = _llenar_tabla(frame, fila, "Top perfumes (por cantidad)", ("Perfume", "Cantidad"), resumen["top_cantidad"])
    fila = _llenar_tabla(frame, fila, "Top perfumes (por dinero)", ("Perfume", "Total"), resumen["top_dinero"])
    fila = _llenar_tabla(frame, fila, "Top clientes", ("Cliente", "Total"), resumen["top_clientes"])
    fila = _llenar_tabla(frame, fila, "Menos vendidos", ("Perfume", "Cantidad"), resumen["menos_vendidos"])
    fila = _llenar_tabla(
        frame, fila, f"Stock bajo (≤ {UMBRAL_STOCK_BAJO} unidades)",
        ("Marca", "Perfume", "Existencias"), resumen["stock_bajo"], anchos=(140, 160, 100)
    )
    fila = _llenar_tabla(
        frame, fila, f"Prediccion de agotamiento (velocidad de los ultimos {DIAS_VELOCIDAD_VENTA} dias)",
        ("Perfume", "Existencias", "Dias estimados restantes"), resumen["dias_restantes"], anchos=(180, 100, 180)
    )
