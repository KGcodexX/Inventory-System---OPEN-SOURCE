"""Pantalla y operaciones de Proveedores y Pedidos (compras)."""
import tkinter as tk
from tkinter import ttk, messagebox

import auth
from config import BG_COLOR, BTN_PADX, BTN_PADY
from db import conexion, cursor
from inventario import cargar_datos
from sheets import exportar_todo_async
from widgets import autocompletar, boton

tabla_proveedores = None


def cargar_proveedores():
    for fila in tabla_proveedores.get_children():
        tabla_proveedores.delete(fila)
    cursor.execute("SELECT * FROM proveedores")
    for row in cursor.fetchall():
        tabla_proveedores.insert("", "end", values=row)


def ventana_agregar_proveedor():
    v = tk.Toplevel()
    v.title("Agregar proveedor")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    labels = ["Nombre", "Telefono", "Correo"]
    entries = []
    for i, l in enumerate(labels):
        tk.Label(frame, text=l).grid(row=i, column=0)
        e = tk.Entry(frame)
        e.grid(row=i, column=1)
        entries.append(e)

    def guardar():
        datos = [e.get() for e in entries]
        cursor.execute("INSERT INTO proveedores (nombre,telefono,correo) VALUES (?,?,?)", datos)
        conexion.commit()
        cargar_proveedores()
        exportar_todo_async()
        v.destroy()

    boton(frame, "Guardar", guardar).grid(row=3, columnspan=2, padx=BTN_PADX, pady=BTN_PADY)


def ventana_editar_proveedor():
    if not auth.es_admin():
        messagebox.showerror("Permiso denegado", "Solo un administrador puede editar proveedores")
        return

    sel = tabla_proveedores.focus()
    if not sel:
        messagebox.showwarning("Aviso", "Selecciona un proveedor")
        return

    valores = tabla_proveedores.item(sel)["values"]

    v = tk.Toplevel()
    v.title("Editar proveedor")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    labels = ["Nombre", "Telefono", "Correo"]
    entries = []

    for i, l in enumerate(labels):
        tk.Label(frame, text=l).grid(row=i, column=0)
        e = tk.Entry(frame)
        e.insert(0, valores[i + 1])
        e.grid(row=i, column=1)
        entries.append(e)

    def actualizar():
        datos = [e.get() for e in entries]
        cursor.execute("""UPDATE proveedores SET
        nombre=?, telefono=?, correo=?
        WHERE id=?""", datos + [valores[0]])
        conexion.commit()
        cargar_proveedores()
        exportar_todo_async()
        v.destroy()

    boton(frame, "Actualizar", actualizar).grid(row=3, columnspan=2, padx=BTN_PADX, pady=BTN_PADY)


def ventana_registrar_compra():
    v = tk.Toplevel()
    v.title("Nuevo pedido")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    cursor.execute("SELECT id,nombre FROM proveedores")
    proveedores = [f"{p[0]} - {p[1]}" for p in cursor.fetchall()]

    cursor.execute("SELECT id,nombre FROM inventario")
    perfumes = [f"{p[0]} - {p[1]}" for p in cursor.fetchall()]

    tk.Label(frame, text="Proveedor").grid(row=0, column=0)
    combo_prov = ttk.Combobox(frame, values=proveedores)
    combo_prov.grid(row=0, column=1)

    tk.Label(frame, text="Perfume").grid(row=1, column=0)
    combo_perf = ttk.Combobox(frame, values=perfumes)
    combo_perf.grid(row=1, column=1)
    combo_perf.bind("<KeyRelease>", lambda e: autocompletar(e, combo_perf, perfumes))

    tk.Label(frame, text="Cantidad").grid(row=2, column=0)
    entry_cant = tk.Entry(frame)
    entry_cant.grid(row=2, column=1)

    tk.Label(frame, text="Costo unitario").grid(row=3, column=0)
    entry_costo = tk.Entry(frame)
    entry_costo.grid(row=3, column=1)

    tabla_temp = ttk.Treeview(frame, columns=("Perfume", "Cantidad", "Costo", "Total"), show="headings")
    for col in ("Perfume", "Cantidad", "Costo", "Total"):
        tabla_temp.heading(col, text=col)
    tabla_temp.grid(row=5, column=0, columnspan=2)

    lista = []

    def agregar():
        try:
            perfume_id = int(combo_perf.get().split(" - ")[0])
            nombre = combo_perf.get().split(" - ")[1]
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Selecciona un perfume valido")
            return

        try:
            cantidad = int(entry_cant.get())
            costo = float(entry_costo.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad y costo deben ser numeros")
            return

        total = cantidad * costo
        lista.append((perfume_id, cantidad, costo, total))
        tabla_temp.insert("", "end", values=(nombre, cantidad, costo, total))

    def guardar_compra():
        if not lista:
            messagebox.showerror("Error", "Agrega al menos un perfume al pedido")
            return

        try:
            prov_id = int(combo_prov.get().split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Selecciona un proveedor valido")
            return

        total = sum(x[3] for x in lista)

        cursor.execute("INSERT INTO compras (proveedor_id,total) VALUES (?,?)", (prov_id, total))
        compra_id = cursor.lastrowid

        for perfume_id, cantidad, costo, total in lista:
            cursor.execute("""
                INSERT INTO detalle_compra
                (compra_id,perfume_id,cantidad,costo_unitario,total)
                 VALUES (?,?,?,?,?)
            """, (compra_id, perfume_id, cantidad, costo, total))

            cursor.execute("""
                UPDATE inventario
                SET existencias=existencias+?, costo_actual=?
                WHERE id=?
            """, (cantidad, costo, perfume_id))

            cursor.execute("""
                INSERT INTO lote_inventario
                (perfume_id, cantidad, unidades_disponibles, costo_unitario)
                VALUES (?,?,?,?)
            """, (perfume_id, cantidad, cantidad, costo))

        conexion.commit()
        cargar_datos()
        exportar_todo_async()
        v.destroy()

    boton(frame, "Agregar", agregar).grid(row=4, column=0, padx=BTN_PADX, pady=BTN_PADY)
    boton(frame, "Guardar pedido", guardar_compra, width=18).grid(row=4, column=1, padx=BTN_PADX, pady=BTN_PADY)


def mostrar_historial_pedidos():
    v = tk.Toplevel()
    v.title("Historial de pedidos")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    tabla_pedidos = ttk.Treeview(v, columns=("ID", "Proveedor", "Fecha", "Total"), show="headings")
    for col in ("ID", "Proveedor", "Fecha", "Total"):
        tabla_pedidos.heading(col, text=col)
        tabla_pedidos.column(col, width=120)
    tabla_pedidos.pack(side="left", fill="both", expand=True)

    tabla_detalle = ttk.Treeview(v, columns=("Perfume", "Cantidad", "Costo", "Total"), show="headings")
    for col in ("Perfume", "Cantidad", "Costo", "Total"):
        tabla_detalle.heading(col, text=col)
        tabla_detalle.column(col, width=120)
    tabla_detalle.pack(side="right", fill="both", expand=True)

    cursor.execute("""
        SELECT c.id, p.nombre, c.fecha, c.total
        FROM compras c
        JOIN proveedores p ON c.proveedor_id = p.id
        ORDER BY c.fecha DESC
    """)
    for row in cursor.fetchall():
        tabla_pedidos.insert("", "end", values=row)

    def mostrar_detalle_pedido(event):
        for fila in tabla_detalle.get_children():
            tabla_detalle.delete(fila)

        sel = tabla_pedidos.focus()
        if not sel:
            return

        compra_id = tabla_pedidos.item(sel)["values"][0]

        cursor.execute("""
            SELECT i.nombre, d.cantidad, d.costo_unitario, d.total
            FROM detalle_compra d
            JOIN inventario i ON d.perfume_id = i.id
            WHERE d.compra_id = ?
        """, (compra_id,))

        for row in cursor.fetchall():
            tabla_detalle.insert("", "end", values=row)

    tabla_pedidos.bind("<<TreeviewSelect>>", mostrar_detalle_pedido)


def mostrar_proveedores(frame_contenido, configurar_grid_contenido):
    global tabla_proveedores
    for w in frame_contenido.winfo_children():
        w.destroy()

    configurar_grid_contenido(cols=4, filas_expand=(0,))
    columnas = ("ID", "Nombre", "Telefono", "Correo")
    tabla_proveedores = ttk.Treeview(frame_contenido, columns=columnas, show="headings")
    for col in columnas:
        tabla_proveedores.heading(col, text=col)
        tabla_proveedores.column(col, width=150)
    tabla_proveedores.grid(row=0, column=0, columnspan=4, sticky="nsew")

    boton(frame_contenido, "Agregar proveedor", ventana_agregar_proveedor, width=18).grid(
        row=1, column=0, padx=BTN_PADX, pady=BTN_PADY, sticky="e")
    boton(frame_contenido, "Nuevo pedido", ventana_registrar_compra).grid(
        row=1, column=1, padx=BTN_PADX, pady=BTN_PADY)
    boton(frame_contenido, "Editar proveedor", ventana_editar_proveedor, width=18).grid(
        row=1, column=2, padx=BTN_PADX, pady=BTN_PADY)
    boton(frame_contenido, "Historial pedidos", mostrar_historial_pedidos, width=18).grid(
        row=1, column=3, padx=BTN_PADX, pady=BTN_PADY, sticky="w")

    cargar_proveedores()
