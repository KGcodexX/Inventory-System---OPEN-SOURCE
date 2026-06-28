"""Ventana principal: menu lateral, contenido y pantalla de inicio."""
import tkinter as tk
from tkinter import ttk, messagebox
import auth
import sheets

from config import BG_COLOR, BTN_BG, BTN_FG, BTN_HOVER, FONT, FONT_BOLD, FRAME_MENU_BG, TEXT_COLOR
from clientes import mostrar_clientes
from economia import abrir_economia
from inventario import mostrar_inventario
from proveedores import mostrar_proveedores
from styles import configurar_estilos, configurar_opciones_globales
from usuarios import mostrar_usuarios
from ventas import mostrar_ventas
from widgets import cargar_imagen_inicio

frame_contenido = None


def configurar_grid_contenido(cols=3, filas_expand=(1,)):
    for i in range(cols):
        frame_contenido.grid_columnconfigure(i, weight=1)
    for r in range(0, 6):
        frame_contenido.grid_rowconfigure(r, weight=1 if r in filas_expand else 0)


def pantalla_inicio():
    for w in frame_contenido.winfo_children():
        w.destroy()
    tk.Label(frame_contenido, text="Bienvenido al Sistema de Perfumeria",
             font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=30)
    img = cargar_imagen_inicio(frame_contenido)
    if img:
        tk.Label(frame_contenido, image=img, bg=BG_COLOR).pack(pady=6)
    tk.Label(frame_contenido, text="Selecciona una opcion del menu lateral para empezar.",
             font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=6)


def crear_ventana_principal():
    global frame_contenido

    root = tk.Tk()
    root.title("Sistema de Perfumeria")
    root.geometry("1150x680")
    root.minsize(1000, 600)
    root.configure(bg=BG_COLOR)

    configurar_opciones_globales(root)

    style = ttk.Style(root)
    configurar_estilos(style)

    frame_menu = tk.Frame(root, bg=FRAME_MENU_BG)
    frame_menu.pack(side="left", fill="y")

    sesion = auth.sesion_actual
    tk.Label(
        frame_menu,
        text=f"{sesion['usuario']} ({sesion['rol']})",
        bg=FRAME_MENU_BG, fg=TEXT_COLOR, font=FONT, wraplength=160, justify="center"
    ).pack(pady=(12, 6))

    frame_contenido = tk.Frame(root, bg=BG_COLOR)
    frame_contenido.pack(side="right", fill="both", expand=True)

    def on_enter(e):
        e.widget["bg"] = BTN_HOVER

    def on_leave(e):
        e.widget["bg"] = BTN_BG

    def crear_boton_menu(texto, comando):
        b = tk.Button(frame_menu, text=texto, width=18, height=1, bg=BTN_BG, fg=BTN_FG,
                      activebackground=BTN_HOVER, font=FONT_BOLD, command=comando, bd=0, relief="ridge")
        b.pack(pady=6)
        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        return b

    crear_boton_menu("INICIO", pantalla_inicio)
    crear_boton_menu("INVENTARIO", lambda: mostrar_inventario(frame_contenido, configurar_grid_contenido))
    crear_boton_menu("VENTAS", lambda: mostrar_ventas(frame_contenido, configurar_grid_contenido))
    crear_boton_menu("CLIENTES", lambda: mostrar_clientes(frame_contenido, configurar_grid_contenido))
    crear_boton_menu("ECONOMIA", abrir_economia)
    crear_boton_menu("PROVEEDORES", lambda: mostrar_proveedores(frame_contenido, configurar_grid_contenido))

    if auth.es_admin():
        crear_boton_menu("USUARIOS", lambda: mostrar_usuarios(frame_contenido, configurar_grid_contenido))

    pantalla_inicio()

    if not sheets.SHEETS_HABILITADO:
        root.after(300, lambda: messagebox.showinfo(
            "Sincronizacion desactivada",
            "No se encontraron credenciales validas de Google Sheets.\n"
            "La app funciona normalmente, pero no se sincronizara con la hoja de calculo."
        ))

    return root
