"""Ventana principal: menu lateral, contenido y pantalla de inicio."""
import tkinter as tk
from tkinter import ttk, messagebox
import auth
import sheets

from config import (
    BG_COLOR, BTN_BG, BTN_FG, BTN_HOVER, CARD_BG,
    FONT, FONT_BOLD, FRAME_MENU_BG, TEXT_COLOR,
)
from clientes import mostrar_clientes
from economia import abrir_economia, obtener_resumen
from inventario import mostrar_inventario
import preferencias
from proveedores import mostrar_proveedores
from styles import configurar_estilos, configurar_opciones_globales
from usuarios import mostrar_usuarios
from ventas import mostrar_ventas
from widgets import boton, cargar_imagen_inicio

frame_contenido = None


def configurar_grid_contenido(cols=3, filas_expand=(1,)):
    for i in range(cols):
        frame_contenido.grid_columnconfigure(i, weight=1)
    for r in range(0, 6):
        frame_contenido.grid_rowconfigure(r, weight=1 if r in filas_expand else 0)


def _tarjeta_resumen(parent, titulo, valor):
    contenedor = tk.Frame(parent, bg=CARD_BG, padx=14, pady=10)
    tk.Label(contenedor, text=titulo, bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 9)).pack(anchor="w")
    tk.Label(contenedor, text=valor, bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 18, "bold")).pack(anchor="w")
    return contenedor


def _construir_tarjetas_resumen(parent):
    try:
        resumen = obtener_resumen()
    except Exception:
        return

    fila = tk.Frame(parent, bg=BG_COLOR)
    fila.pack(pady=(0, 24))

    tarjetas = [
        ("Ventas hoy", str(resumen["ventas_hoy"])),
        ("Total vendido hoy", f"${resumen['total_hoy']:.2f}"),
        ("Ganancia hoy", f"${resumen['ganancia_hoy']:.2f}"),
        ("Perfumes con stock bajo", str(len(resumen["stock_bajo"]))),
    ]

    for i, (titulo, valor) in enumerate(tarjetas):
        _tarjeta_resumen(fila, titulo, valor).grid(row=0, column=i, padx=8)


def _alternar_notificaciones():
    preferencias.alternar_notificaciones()
    pantalla_inicio()


def pantalla_inicio():
    for w in frame_contenido.winfo_children():
        w.destroy()

    tk.Label(frame_contenido, text="Bienvenido al Sistema de Perfumeria",
             font=("Segoe UI", 18, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(30, 4))
    tk.Label(frame_contenido, text="Selecciona una opcion del menu lateral para empezar.",
             font=FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(0, 20))

    _construir_tarjetas_resumen(frame_contenido)

    contenedor_imagen = tk.Frame(frame_contenido, bg=BG_COLOR)
    contenedor_imagen.pack(fill="both", expand=True, pady=(0, 12))

    img = cargar_imagen_inicio(contenedor_imagen)
    if img:
        tk.Label(contenedor_imagen, image=img, bg=BG_COLOR).place(relx=0.5, rely=0.5, anchor="center")

    texto_boton = (
        "Desactivar notificaciones de stock bajo" if preferencias.notificaciones_activas()
        else "Activar notificaciones de stock bajo"
    )
    boton(frame_contenido, texto_boton, _alternar_notificaciones, width=32).pack(pady=(0, 16))


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
        b = tk.Button(frame_menu, text=texto, width=20, height=2, bg=BTN_BG, fg=BTN_FG,
                      activebackground=BTN_HOVER, font=("Segoe UI", 12, "bold"), command=comando,
                      bd=0, relief="ridge", cursor="hand2")
        b.pack(pady=8, padx=12)
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

    if preferencias.notificaciones_activas():
        root.after(600, _avisar_stock_bajo)

    return root


def _avisar_stock_bajo():
    try:
        resumen = obtener_resumen()
    except Exception:
        return

    stock_bajo = resumen["stock_bajo"]
    if not stock_bajo:
        return

    detalle = "\n".join(f"- {marca} {nombre} ({existencias} unidades)" for marca, nombre, existencias in stock_bajo)
    messagebox.showwarning(
        "Stock bajo",
        f"Hay {len(stock_bajo)} perfume(s) con pocas existencias:\n\n{detalle}"
    )
