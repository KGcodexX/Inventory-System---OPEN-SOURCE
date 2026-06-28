"""Pantalla de inicio de sesion y creacion de la primera cuenta admin."""
import tkinter as tk
from tkinter import messagebox

import auth
from config import BG_COLOR
from widgets import boton, entry, label


def mostrar_login():
    resultado = {"ok": False}

    ventana = tk.Tk()
    ventana.title("Iniciar sesion")
    ventana.configure(bg=BG_COLOR)
    ventana.resizable(False, False)

    frame = tk.Frame(ventana, bg=BG_COLOR)
    frame.pack(padx=24, pady=24)

    if not auth.hay_usuarios():
        _formulario_primer_admin(frame, ventana, resultado)
    else:
        _formulario_login(frame, ventana, resultado)

    ventana.mainloop()
    return resultado["ok"]


def _formulario_login(frame, ventana, resultado):
    label(frame, "Bienvenido, inicia sesion").grid(row=0, column=0, columnspan=2, pady=(0, 12))

    label(frame, "Usuario").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
    entry_usuario = entry(frame)
    entry_usuario.grid(row=1, column=1, pady=6)

    label(frame, "Contraseña").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=6)
    entry_password = entry(frame)
    entry_password.config(show="*")
    entry_password.grid(row=2, column=1, pady=6)

    def intentar_login():
        usuario = entry_usuario.get().strip()
        password = entry_password.get()

        if not usuario or not password:
            messagebox.showerror("Error", "Completa usuario y contraseña")
            return

        rol = auth.verificar_credenciales(usuario, password)
        if rol is None:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            return

        auth.iniciar_sesion(usuario, rol)
        resultado["ok"] = True
        ventana.destroy()

    boton(frame, "Entrar", intentar_login, width=20).grid(row=3, column=0, columnspan=2, pady=(12, 0))
    entry_password.bind("<Return>", lambda e: intentar_login())


def _formulario_primer_admin(frame, ventana, resultado):
    label(frame, "Primera vez: crea la cuenta de administrador").grid(row=0, column=0, columnspan=2, pady=(0, 12))

    label(frame, "Usuario").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
    entry_usuario = entry(frame)
    entry_usuario.grid(row=1, column=1, pady=6)

    label(frame, "Contraseña").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=6)
    entry_password = entry(frame)
    entry_password.config(show="*")
    entry_password.grid(row=2, column=1, pady=6)

    label(frame, "Confirmar contraseña").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
    entry_password_confirmar = entry(frame)
    entry_password_confirmar.config(show="*")
    entry_password_confirmar.grid(row=3, column=1, pady=6)

    def crear_admin():
        usuario = entry_usuario.get().strip()
        password = entry_password.get()
        password_confirmar = entry_password_confirmar.get()

        if not usuario or not password:
            messagebox.showerror("Error", "Completa usuario y contraseña")
            return

        if password != password_confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return

        if len(password) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
            return

        auth.crear_usuario(usuario, password, "admin")
        auth.iniciar_sesion(usuario, "admin")
        resultado["ok"] = True
        ventana.destroy()

    boton(frame, "Crear cuenta", crear_admin, width=20).grid(row=4, column=0, columnspan=2, pady=(12, 0))
