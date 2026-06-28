"""Pantalla y operaciones de Inventario."""
import tkinter as tk
from tkinter import ttk, messagebox

import auth
from config import BG_COLOR, BTN_PADX, BTN_PADY
from db import conexion, cursor, resecuenciar_ids_inventario, respaldar_base_datos
from sheets import exportar_todo_async
from widgets import boton

tabla = None
entry_buscar = None


def cargar_datos(filtro=""):
    global tabla
    if tabla is None or not tabla.winfo_exists():
        return

    for fila in tabla.get_children():
        tabla.delete(fila)

    if filtro:
        cursor.execute(
            "SELECT * FROM inventario WHERE nombre LIKE ? ORDER BY marca COLLATE NOCASE, nombre COLLATE NOCASE",
            (f"%{filtro}%",)
        )
    else:
        cursor.execute("SELECT * FROM inventario ORDER BY marca COLLATE NOCASE, nombre COLLATE NOCASE")

    for row in cursor.fetchall():
        tabla.insert("", "end", values=row)


def ventana_agregar():
    v = tk.Toplevel()
    v.title("Agregar perfume")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    campos = ["Marca", "Sexo", "Nombre", "Mililitros", "Precio", "Precio Mayoreo", "Existencias"]
    entradas = []

    for i, c in enumerate(campos):
        tk.Label(frame, text=c).grid(row=i, column=0)
        e = tk.Entry(frame)
        e.grid(row=i, column=1)
        entradas.append(e)

    def guardar():
        valores = [e.get() for e in entradas]
        marca, sexo, nombre = valores[0], valores[1], valores[2]

        try:
            mililitros = float(valores[3])
            precio = float(valores[4])
            precio_mayoreo = float(valores[5])
            existencias = int(valores[6])
        except ValueError:
            messagebox.showerror("Error", "Mililitros, Precio, Precio Mayoreo y Existencias deben ser numeros")
            return

        cursor.execute("""INSERT INTO inventario
        (marca,sexo,nombre,mililitros,precio,precio_mayoreo,existencias)
        VALUES (?,?,?,?,?,?,?)""", (marca, sexo, nombre, mililitros, precio, precio_mayoreo, existencias))
        conexion.commit()
        cargar_datos()
        exportar_todo_async()
        v.destroy()

    boton(frame, "Guardar", guardar).grid(row=7, columnspan=2, padx=BTN_PADX, pady=BTN_PADY)


def ventana_editar():
    if not auth.es_admin():
        messagebox.showerror("Permiso denegado", "Solo un administrador puede editar perfumes")
        return

    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Aviso", "Selecciona un perfume")
        return
    valores = tabla.item(seleccionado)["values"]

    v = tk.Toplevel()
    v.title("Editar perfume")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    campos = ["Marca", "Sexo", "Nombre", "Mililitros", "Precio", "Precio Mayoreo", "Existencias"]
    entradas = []

    for i, c in enumerate(campos):
        tk.Label(frame, text=c).grid(row=i, column=0)
        e = tk.Entry(frame)
        e.insert(0, valores[i + 1])
        e.grid(row=i, column=1)
        entradas.append(e)

    def actualizar():
        entradas_valores = [e.get() for e in entradas]
        marca, sexo, nombre = entradas_valores[0], entradas_valores[1], entradas_valores[2]

        try:
            mililitros = float(entradas_valores[3])
            precio = float(entradas_valores[4])
            precio_mayoreo = float(entradas_valores[5])
            existencias = int(entradas_valores[6])
        except ValueError:
            messagebox.showerror("Error", "Mililitros, Precio, Precio Mayoreo y Existencias deben ser numeros")
            return

        cursor.execute("""UPDATE inventario SET
        marca=?,sexo=?,nombre=?,mililitros=?,
        precio=?,precio_mayoreo=?,existencias=?
        WHERE id=?""", (marca, sexo, nombre, mililitros, precio, precio_mayoreo, existencias, valores[0]))
        conexion.commit()
        cargar_datos()
        exportar_todo_async()
        v.destroy()

    boton(frame, "Actualizar", actualizar).grid(row=7, columnspan=2, padx=BTN_PADX, pady=BTN_PADY)


def eliminar_perfume():
    if not auth.es_admin():
        messagebox.showerror("Permiso denegado", "Solo un administrador puede eliminar perfumes")
        return

    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showwarning("Aviso", "Selecciona un perfume")
        return
    valores = tabla.item(seleccionado)["values"]
    perfume_id = valores[0]
    if not messagebox.askyesno("Confirmar", f"¿Eliminar el perfume '{valores[3]}'?"):
        return
    respaldar_base_datos()
    cursor.execute("DELETE FROM inventario WHERE id=?", (perfume_id,))
    resecuenciar_ids_inventario()
    conexion.commit()
    exportar_todo_async()
    cargar_datos()


def mostrar_inventario(frame_contenido, configurar_grid_contenido):
    global tabla, entry_buscar
    for w in frame_contenido.winfo_children():
        w.destroy()

    configurar_grid_contenido(cols=3, filas_expand=(1,))

    tk.Label(frame_contenido, text="Buscar perfume:").grid(row=0, column=0)
    entry_buscar = tk.Entry(frame_contenido)
    entry_buscar.grid(row=0, column=1, sticky="ew")
    boton(frame_contenido, "Buscar", lambda: cargar_datos(entry_buscar.get())).grid(
        row=0, column=2, padx=BTN_PADX, pady=BTN_PADY, sticky="e")

    columnas = ("ID", "Marca", "Sexo", "Nombre", "ML", "Precio", "Precio Mayoreo", "Existencias")
    tabla = ttk.Treeview(frame_contenido, columns=columnas, show="headings")
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120)
    tabla.grid(row=1, column=0, columnspan=3, sticky="nsew")

    boton(frame_contenido, "Agregar", ventana_agregar).grid(row=2, column=0, padx=BTN_PADX, pady=BTN_PADY, sticky="e")
    boton(frame_contenido, "Editar", ventana_editar).grid(row=2, column=1, padx=BTN_PADX, pady=BTN_PADY)
    boton(frame_contenido, "Eliminar", eliminar_perfume).grid(row=2, column=2, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
    cargar_datos()
