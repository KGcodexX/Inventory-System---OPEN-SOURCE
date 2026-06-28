"""Pantalla de gestion de usuarios (solo accesible para administradores)."""
import tkinter as tk
from tkinter import ttk, messagebox

import auth
from config import BG_COLOR, BTN_PADX, BTN_PADY
from db import conexion, cursor
from widgets import boton

tabla_usuarios = None


def cargar_usuarios():
    for fila in tabla_usuarios.get_children():
        tabla_usuarios.delete(fila)
    cursor.execute("SELECT usuario, rol FROM usuarios ORDER BY usuario")
    for row in cursor.fetchall():
        tabla_usuarios.insert("", "end", values=row)


def ventana_crear_usuario():
    v = tk.Toplevel()
    v.title("Crear usuario")
    v.configure(bg=BG_COLOR)
    frame = tk.Frame(v, bg=BG_COLOR)
    frame.pack(padx=12, pady=12)

    tk.Label(frame, text="Usuario").grid(row=0, column=0)
    entry_usuario = tk.Entry(frame)
    entry_usuario.grid(row=0, column=1)

    tk.Label(frame, text="Contraseña").grid(row=1, column=0)
    entry_password = tk.Entry(frame, show="*")
    entry_password.grid(row=1, column=1)

    tk.Label(frame, text="Rol").grid(row=2, column=0)
    combo_rol = ttk.Combobox(frame, values=list(auth.ROLES), state="readonly")
    combo_rol.current(1)
    combo_rol.grid(row=2, column=1)

    def guardar():
        usuario = entry_usuario.get().strip()
        password = entry_password.get()
        rol = combo_rol.get()

        if not usuario or not password:
            messagebox.showerror("Error", "Completa usuario y contraseña")
            return

        if len(password) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
            return

        try:
            auth.crear_usuario(usuario, password, rol)
        except Exception:
            messagebox.showerror("Error", "Ese nombre de usuario ya existe")
            return

        cargar_usuarios()
        v.destroy()

    boton(frame, "Guardar", guardar).grid(row=3, columnspan=2, padx=BTN_PADX, pady=BTN_PADY)


def eliminar_usuario():
    sel = tabla_usuarios.focus()
    if not sel:
        messagebox.showwarning("Aviso", "Selecciona un usuario")
        return

    usuario = tabla_usuarios.item(sel)["values"][0]

    if usuario == auth.sesion_actual["usuario"]:
        messagebox.showerror("Error", "No puedes eliminar tu propia cuenta mientras tienes sesion activa")
        return

    if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{usuario}'?"):
        cursor.execute("DELETE FROM usuarios WHERE usuario=?", (usuario,))
        conexion.commit()
        cargar_usuarios()


def mostrar_usuarios(frame_contenido, configurar_grid_contenido):
    global tabla_usuarios
    for w in frame_contenido.winfo_children():
        w.destroy()

    configurar_grid_contenido(cols=3, filas_expand=(0,))
    columnas = ("Usuario", "Rol")
    tabla_usuarios = ttk.Treeview(frame_contenido, columns=columnas, show="headings")
    for col in columnas:
        tabla_usuarios.heading(col, text=col)
        tabla_usuarios.column(col, width=200)
    tabla_usuarios.grid(row=0, column=0, columnspan=3, sticky="nsew")

    boton(frame_contenido, "Crear usuario", ventana_crear_usuario, width=18).grid(
        row=1, column=0, padx=BTN_PADX, pady=BTN_PADY, sticky="e")
    boton(frame_contenido, "Eliminar usuario", eliminar_usuario, width=18).grid(
        row=1, column=1, padx=BTN_PADX, pady=BTN_PADY)

    cargar_usuarios()
