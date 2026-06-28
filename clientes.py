"""Pantalla y operaciones de Clientes."""
import tkinter as tk
from tkinter import ttk, messagebox

import auth
from config import BG_COLOR, BTN_PADX, BTN_PADY
from db import conexion, cursor, respaldar_base_datos
from sheets import exportar_todo_async
from widgets import boton

tabla_clientes = None


def cargar_clientes():
    for fila in tabla_clientes.get_children():
        tabla_clientes.delete(fila)
    cursor.execute("SELECT * FROM clientes")
    for row in cursor.fetchall():
        tabla_clientes.insert("", "end", values=row)


def ventana_agregar_cliente():
    v = tk.Toplevel()
    v.title("Agregar cliente")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    labels = ["Nombre", "Telefono", "Correo", "Tipo"]
    entries = []
    for i, l in enumerate(labels):
        tk.Label(frame, text=l).grid(row=i, column=0)
        e = tk.Entry(frame)
        e.grid(row=i, column=1)
        entries.append(e)

    def guardar():
        datos = [e.get() for e in entries]
        cursor.execute("INSERT INTO clientes (nombre,telefono,correo,tipo) VALUES (?,?,?,?)", datos)
        conexion.commit()
        cargar_clientes()
        exportar_todo_async()
        v.destroy()

    boton(frame, "Guardar", guardar).grid(row=4, columnspan=2, padx=BTN_PADX, pady=BTN_PADY)


def eliminar_cliente():
    if not auth.es_admin():
        messagebox.showerror("Permiso denegado", "Solo un administrador puede eliminar clientes")
        return

    sel = tabla_clientes.focus()
    if not sel:
        return
    idc = tabla_clientes.item(sel)["values"][0]
    if messagebox.askyesno("Confirmar", "¿Eliminar cliente?"):
        respaldar_base_datos()
        cursor.execute("DELETE FROM clientes WHERE id=?", (idc,))
        conexion.commit()
        cargar_clientes()
        exportar_todo_async()


def historial_compras_cliente():
    sel = tabla_clientes.focus()
    if not sel:
        messagebox.showwarning("Aviso", "Selecciona un cliente")
        return

    cliente_id = tabla_clientes.item(sel)["values"][0]
    cliente_nombre = tabla_clientes.item(sel)["values"][1]

    v = tk.Toplevel()
    v.title(f"Historial de compras - {cliente_nombre}")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    tk.Label(v, text=f"Historial de compras de {cliente_nombre}", font=("Arial", 14, "bold")).pack(pady=10)

    tabla_historial = ttk.Treeview(v, columns=("VentaID", "Fecha", "Perfume", "Cantidad", "Tipo", "Total"), show="headings")
    for col in ("VentaID", "Fecha", "Perfume", "Cantidad", "Tipo", "Total"):
        tabla_historial.heading(col, text=col)
        tabla_historial.column(col, width=120)
    tabla_historial.pack(fill="both", expand=True)

    cursor.execute("""
        SELECT v.id, v.fecha, COALESCE(d.nombre_perfume, i.nombre), d.cantidad, d.tipo_precio, d.total
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        LEFT JOIN inventario i ON d.perfume_id=i.id
        WHERE v.cliente_id=?
        ORDER BY v.fecha DESC
    """, (cliente_id,))

    for row in cursor.fetchall():
        tabla_historial.insert("", "end", values=row)


def mostrar_clientes(frame_contenido, configurar_grid_contenido):
    global tabla_clientes
    for w in frame_contenido.winfo_children():
        w.destroy()

    configurar_grid_contenido(cols=3, filas_expand=(0,))
    columnas = ("ID", "Nombre", "Telefono", "Correo", "Tipo")
    tabla_clientes = ttk.Treeview(frame_contenido, columns=columnas, show="headings")
    for col in columnas:
        tabla_clientes.heading(col, text=col)
        tabla_clientes.column(col, width=150)
    tabla_clientes.grid(row=0, column=0, columnspan=3, sticky="nsew")

    boton(frame_contenido, "Agregar cliente", ventana_agregar_cliente).grid(
        row=1, column=0, padx=BTN_PADX, pady=BTN_PADY, sticky="e")
    boton(frame_contenido, "Eliminar cliente", eliminar_cliente).grid(
        row=1, column=1, padx=BTN_PADX, pady=BTN_PADY)
    boton(frame_contenido, "Historial compras", historial_compras_cliente, width=18).grid(
        row=1, column=2, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
    cargar_clientes()
