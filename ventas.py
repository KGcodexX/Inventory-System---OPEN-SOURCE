"""Pantalla y operaciones de Ventas."""
import os
import tkinter as tk
from tkinter import ttk, messagebox

import auth
from config import BG_COLOR, BTN_PADX, BTN_PADY, CARD_BG, FONT_SMALL, TEXT_COLOR
from db import conexion, cursor, respaldar_base_datos
from inventario import cargar_datos
from recibos import generar_recibo_pdf
from sheets import exportar_todo_async
from widgets import autocompletar, boton, entry, label

tabla_ventas = None
tabla_detalle = None
entry_buscar_venta = None


def cargar_ventas(filtro="", fecha_desde="", fecha_hasta=""):
    global tabla_ventas
    if tabla_ventas is None or not tabla_ventas.winfo_exists():
        return

    for fila in tabla_ventas.get_children():
        tabla_ventas.delete(fila)

    condiciones = []
    parametros = []

    if filtro:
        condiciones.append("c.nombre LIKE ?")
        parametros.append(f"%{filtro}%")

    if fecha_desde:
        condiciones.append("DATE(v.fecha) >= DATE(?)")
        parametros.append(fecha_desde)

    if fecha_hasta:
        condiciones.append("DATE(v.fecha) <= DATE(?)")
        parametros.append(fecha_hasta)

    consulta = "SELECT v.id,c.nombre,v.fecha FROM ventas v JOIN clientes c ON v.cliente_id=c.id"
    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)

    try:
        cursor.execute(consulta, parametros)
    except Exception:
        messagebox.showerror("Error", "Fecha invalida, usa el formato AAAA-MM-DD")
        return

    for row in cursor.fetchall():
        tabla_ventas.insert("", "end", values=row)


def mostrar_detalle(event):
    for fila in tabla_detalle.get_children():
        tabla_detalle.delete(fila)

    sel = tabla_ventas.focus()
    if not sel:
        return
    venta_id = tabla_ventas.item(sel)["values"][0]

    cursor.execute("""SELECT d.nombre_perfume,
                         d.cantidad,
                         d.tipo_precio,
                         d.total,
                         v.metodo_pago
    FROM detalle_venta d
    JOIN ventas v ON d.venta_id = v.id
    WHERE d.venta_id=?""", (venta_id,))

    for row in cursor.fetchall():
        tabla_detalle.insert("", "end", values=row)


def eliminar_venta():
    if not auth.es_admin():
        messagebox.showerror("Permiso denegado", "Solo un administrador puede eliminar ventas")
        return

    sel = tabla_ventas.focus()
    if not sel:
        return
    venta_id = tabla_ventas.item(sel)["values"][0]

    if messagebox.askyesno("Confirmar", "¿Eliminar esta venta?"):
        respaldar_base_datos()

        # Recuperar perfumes y cantidades de la venta
        cursor.execute("SELECT perfume_id, cantidad FROM detalle_venta WHERE venta_id=?", (venta_id,))
        perfumes_venta = cursor.fetchall()

        # Devolver al inventario
        for perfume_id, cantidad in perfumes_venta:
            cursor.execute("UPDATE inventario SET existencias = existencias + ? WHERE id=?",
                           (cantidad, perfume_id))
            revertir_descuento_lotes(perfume_id, cantidad)

        # Borrar detalle y venta
        cursor.execute("DELETE FROM detalle_venta WHERE venta_id=?", (venta_id,))
        cursor.execute("DELETE FROM ventas WHERE id=?", (venta_id,))

        conexion.commit()
        exportar_todo_async()
        cargar_ventas()


def generar_recibo():
    sel = tabla_ventas.focus()
    if not sel:
        messagebox.showwarning("Aviso", "Selecciona una venta")
        return

    venta_id = tabla_ventas.item(sel)["values"][0]
    ruta = generar_recibo_pdf(venta_id)

    if ruta is None:
        messagebox.showerror("Error", "No se encontro la venta")
        return

    messagebox.showinfo("Recibo generado", f"Recibo guardado en:\n{os.path.abspath(ruta)}")
    try:
        os.startfile(ruta)
    except Exception:
        pass


def calcular_costo_estimado(perfume_id, cantidad_vendida):
    cursor.execute("""
        SELECT unidades_disponibles, costo_unitario
        FROM lote_inventario
        WHERE perfume_id = ? AND unidades_disponibles > 0
        ORDER BY fecha_compra ASC
    """, (perfume_id,))

    lotes = cursor.fetchall()
    costo_total = 0
    cantidad_restante = cantidad_vendida

    for disponibles, costo_unit in lotes:
        if cantidad_restante <= 0:
            break
        usar = min(disponibles, cantidad_restante)
        costo_total += usar * costo_unit
        cantidad_restante -= usar

    return costo_total


def aplicar_descuento_lotes(perfume_id, cantidad_vendida):
    cursor.execute("""
        SELECT id, unidades_disponibles, costo_unitario
        FROM lote_inventario
        WHERE perfume_id = ? AND unidades_disponibles > 0
        ORDER BY fecha_compra ASC
    """, (perfume_id,))

    lotes = cursor.fetchall()
    costo_total = 0
    cantidad_restante = cantidad_vendida

    for lote_id, disponibles, costo_unit in lotes:
        if cantidad_restante <= 0:
            break
        usar = min(disponibles, cantidad_restante)
        costo_total += usar * costo_unit
        cantidad_restante -= usar

        cursor.execute("""
            UPDATE lote_inventario SET unidades_disponibles = unidades_disponibles - ?
            WHERE id = ?
        """, (usar, lote_id))

    return costo_total

def revertir_descuento_lotes(perfume_id, cantidad_a_restaurar):
    cursor.execute("""
        SELECT id, cantidad, unidades_disponibles
        FROM lote_inventario
        WHERE perfume_id = ?
        ORDER BY fecha_compra ASC
    """, (perfume_id,))

    lotes = cursor.fetchall()
    restante = cantidad_a_restaurar

    for lote_id, cantidad_original, disponibles in lotes:
        if restante <= 0:
            break
        espacio = cantidad_original - disponibles
        if espacio <= 0:
            continue
        restaurar = min(espacio, restante)
        cursor.execute("""
            UPDATE lote_inventario SET unidades_disponibles = unidades_disponibles + ?
            WHERE id = ?
        """, (restaurar, lote_id))
        restante -= restaurar
        
def ventana_registrar_venta():
    v = tk.Toplevel()
    v.title("Registrar venta")
    v.configure(bg=BG_COLOR)
    v.resizable(False, False)

    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=20, pady=20)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_columnconfigure(3, weight=1)

    field_width = 28

    cursor.execute("SELECT id,nombre FROM clientes")
    clientes = [f"{c[0]} - {c[1]}" for c in cursor.fetchall()]

    cursor.execute("SELECT id,nombre FROM inventario")
    perfumes = [f"{p[0]} - {p[1]}" for p in cursor.fetchall()]

    label(frame, "Cliente").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=6)
    combo_cliente = ttk.Combobox(frame, values=clientes, width=field_width)
    combo_cliente.grid(row=0, column=1, sticky="ew", pady=6)
    combo_cliente.bind("<KeyRelease>", lambda e: autocompletar(e, combo_cliente, clientes))

    label(frame, "Metodo de pago").grid(row=0, column=2, sticky="e", padx=(24, 8), pady=6)
    combo_pago = ttk.Combobox(
        frame,
        values=["Efectivo", "Tarjeta", "Transferencia", "Regalo"],
        state="readonly",
        width=field_width,
        style="Pago.TCombobox"
    )
    combo_pago.current(0)
    combo_pago.grid(row=0, column=3, sticky="ew", pady=6)

    label(frame, "Perfume").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
    combo_perfume = ttk.Combobox(frame, values=perfumes, width=field_width)
    combo_perfume.grid(row=1, column=1, sticky="ew", pady=6)
    combo_perfume.bind("<KeyRelease>", lambda e: autocompletar(e, combo_perfume, perfumes))

    label(frame, "Tipo precio").grid(row=1, column=2, sticky="e", padx=(24, 8), pady=6)
    combo_precio = ttk.Combobox(
        frame,
        values=["normal", "mayoreo", "personalizado"],
        width=field_width,
        state="readonly",
        style="Precio.TCombobox"
    )
    combo_precio.current(0)
    combo_precio.grid(row=1, column=3, sticky="ew", pady=6)

    label(frame, "Cantidad").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=6)
    entry_cantidad = entry(frame)
    entry_cantidad.config(width=field_width, font=FONT_SMALL)
    entry_cantidad.grid(row=2, column=1, sticky="ew", pady=6, ipady=3)

    label(frame, "Precio personalizado").grid(row=2, column=2, sticky="e", padx=(24, 8), pady=6)
    entry_precio_personalizado = tk.Entry(
        frame,
        width=field_width,
        state="disabled",
        bg=CARD_BG,
        fg=TEXT_COLOR,
        disabledbackground=CARD_BG,
        disabledforeground=TEXT_COLOR,
        relief="flat"
    )
    entry_precio_personalizado.grid(row=2, column=3, sticky="ew", pady=6, ipady=3)

    def toggle_precio_personalizado(*_):
        if combo_precio.get() == "personalizado":
            entry_precio_personalizado.config(state="normal")
        else:
            entry_precio_personalizado.delete(0, tk.END)
            entry_precio_personalizado.config(state="disabled")

    combo_precio.bind("<<ComboboxSelected>>", toggle_precio_personalizado)

    tabla_temp = ttk.Treeview(frame, columns=("Perfume", "Cantidad", "Precio", "Total"), show="headings", height=8)
    for col in ("Perfume", "Cantidad", "Precio", "Total"):
        tabla_temp.heading(col, text=col)
        tabla_temp.column(col, width=140, anchor="center")
    tabla_temp.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=(16, 10))

    lista = []

    def agregar_perfume():
        if not combo_perfume.get():
            messagebox.showerror("Error", "Selecciona un perfume")
            return

        try:
            perfume_id = int(combo_perfume.get().split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Perfume invalido")
            return

        try:
            cantidad = int(entry_cantidad.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad invalida")
            return

        tipo = combo_precio.get()

        cursor.execute("SELECT nombre,precio,precio_mayoreo,existencias FROM inventario WHERE id=?", (perfume_id,))
        nombre, precio, precio_mayoreo, existencias = cursor.fetchone()

        cantidad_ya_agregada = sum(item[2] for item in lista if item[0] == perfume_id)

        if cantidad_ya_agregada + cantidad > existencias:
            messagebox.showerror("Error", "No hay suficientes existencias")
            return

        costo_real = calcular_costo_estimado(perfume_id, cantidad)
        if tipo == "personalizado":
            try:
                precio_personalizado = float(entry_precio_personalizado.get())
            except ValueError:
                messagebox.showerror("Error", "Precio personalizado inválido")
                return
            if precio_personalizado <= 0:
                messagebox.showerror("Error", "Precio personalizado debe ser mayor a 0")
                return
            total = precio_personalizado * cantidad
            precio_label = f"personalizado {precio_personalizado}"
        else:
            total = precio * cantidad if tipo == "normal" else precio_mayoreo * cantidad
            precio_label = tipo
        ganancia = total - costo_real
        lista.append((perfume_id, nombre, cantidad, tipo, total, costo_real, ganancia))

        tabla_temp.insert("", "end", values=(nombre, cantidad, precio_label, total))

    def guardar_venta():
        if not lista:
            messagebox.showerror("Error", "Agrega al menos un perfume a la venta")
            return

        try:
            cliente_id = int(combo_cliente.get().split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Selecciona un cliente valido")
            return

        metodo_pago = combo_pago.get()

        cursor.execute("INSERT INTO ventas (cliente_id, metodo_pago) VALUES (?,?)", (cliente_id, metodo_pago))
        venta_id = cursor.lastrowid

        detalle_values = []
        update_inventario = []

        cursor.execute("SELECT id, nombre, precio, precio_mayoreo, existencias FROM inventario")
        perfumes_dict = {row[0]: row for row in cursor.fetchall()}

        for perfume_id, nombre_perfume, cantidad, tipo, total, _costo_preview, _ganancia_preview in lista:
            if cantidad > perfumes_dict[perfume_id][4]:
                messagebox.showerror("Error", f"No hay suficientes existencias de {nombre_perfume}")
                return

            costo_real = aplicar_descuento_lotes(perfume_id, cantidad)
            ganancia = total - costo_real

            detalle_values.append((venta_id, perfume_id, nombre_perfume, cantidad, tipo, total, costo_real, ganancia))
            update_inventario.append((cantidad, perfume_id))

        cursor.executemany("""INSERT INTO detalle_venta
            (venta_id, perfume_id, nombre_perfume, cantidad, tipo_precio, total, costo_unitario, ganancia)
             VALUES (?,?,?,?,?,?,?,?)
        """, detalle_values)

        cursor.executemany("UPDATE inventario SET existencias = existencias - ? WHERE id=?", update_inventario)

        conexion.commit()
        cargar_datos()
        cargar_ventas()
        exportar_todo_async()
        v.destroy()

    boton(frame, "Agregar perfume", agregar_perfume, width=18).grid(row=3, column=0, columnspan=2, padx=BTN_PADX, pady=(12, 0), sticky="ew")
    boton(frame, "Guardar venta", guardar_venta, width=18).grid(row=3, column=2, columnspan=2, padx=BTN_PADX, pady=(12, 0), sticky="ew")


def mostrar_ventas(frame_contenido, configurar_grid_contenido):
    global tabla_ventas, tabla_detalle, entry_buscar_venta
    for w in frame_contenido.winfo_children():
        w.destroy()

    configurar_grid_contenido(cols=4, filas_expand=(2,))

    tk.Label(frame_contenido, text="Buscar cliente:").grid(row=0, column=0, sticky="e")
    entry_buscar_venta = tk.Entry(frame_contenido)
    entry_buscar_venta.grid(row=0, column=1, sticky="ew")

    tk.Label(frame_contenido, text="Desde (AAAA-MM-DD):").grid(row=1, column=0, sticky="e")
    entry_fecha_desde = tk.Entry(frame_contenido)
    entry_fecha_desde.grid(row=1, column=1, sticky="ew")

    tk.Label(frame_contenido, text="Hasta (AAAA-MM-DD):").grid(row=1, column=2, sticky="e")
    entry_fecha_hasta = tk.Entry(frame_contenido)
    entry_fecha_hasta.grid(row=1, column=3, sticky="ew")

    def buscar():
        cargar_ventas(entry_buscar_venta.get(), entry_fecha_desde.get().strip(), entry_fecha_hasta.get().strip())

    boton(frame_contenido, "Buscar", buscar).grid(
        row=0, column=2, columnspan=2, padx=BTN_PADX, pady=BTN_PADY, sticky="e")

    columnas = ("ID", "Cliente", "Fecha")
    tabla_ventas = ttk.Treeview(frame_contenido, columns=columnas, show="headings")
    for col in columnas:
        tabla_ventas.heading(col, text=col)
        tabla_ventas.column(col, width=150)
    tabla_ventas.grid(row=2, column=0, columnspan=2, sticky="nsew")
    tabla_ventas.bind("<<TreeviewSelect>>", mostrar_detalle)

    columnas2 = ("Perfume", "Cantidad", "Precio", "Total", "Metodo de pago")
    tabla_detalle = ttk.Treeview(frame_contenido, columns=columnas2, show="headings")
    for col in columnas2:
        tabla_detalle.heading(col, text=col)
        tabla_detalle.column(col, width=120)
    tabla_detalle.grid(row=2, column=2, columnspan=2, sticky="nsew")

    boton(frame_contenido, "Nueva venta", ventana_registrar_venta).grid(
        row=3, column=0, padx=BTN_PADX, pady=BTN_PADY, sticky="e")
    boton(frame_contenido, "Eliminar venta", eliminar_venta).grid(
        row=3, column=1, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
    boton(frame_contenido, "Generar recibo PDF", generar_recibo, width=18).grid(
        row=3, column=2, columnspan=2, padx=BTN_PADX, pady=BTN_PADY, sticky="w")

    cargar_ventas()
