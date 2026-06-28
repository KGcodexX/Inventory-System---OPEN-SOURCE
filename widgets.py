"""Widgets y helpers de UI reutilizables (botones, entradas, autocompletado, imagen de inicio)."""
import tkinter as tk

from PIL import Image, ImageTk

from config import BG_COLOR, BTN_BG, BTN_FG, BTN_HOVER, BTN_WIDTH, CARD_BG, FONT, FONT_BOLD, TEXT_COLOR

img_inicio = None  # referencia global para que la imagen no sea recolectada por el GC


def boton(parent, texto, comando, width=BTN_WIDTH):
    b = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=BTN_BG,
        fg=BTN_FG,
        activebackground=BTN_HOVER,
        activeforeground=BTN_FG,
        font=FONT_BOLD,
        width=width,
        bd=0,
        relief="ridge",
        pady=8,
        cursor="hand2"
    )
    b.bind("<Enter>", lambda e: e.widget.config(bg=BTN_HOVER))
    b.bind("<Leave>", lambda e: e.widget.config(bg=BTN_BG))
    return b


def label(parent, texto):
    return tk.Label(
        parent,
        text=texto,
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=FONT
    )


def entry(parent):
    return tk.Entry(
        parent,
        bg=CARD_BG,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
        relief="flat",
        font=FONT,
        width=25
    )


def autocompletar(event, combobox, lista_original):
    texto = combobox.get().lower()
    coincidencias = [item for item in lista_original if texto in item.lower()]
    combobox["values"] = coincidencias
    if coincidencias:
        combobox.event_generate("<Down>")


def cargar_imagen_inicio(parent, max_w=600, max_h=400):
    global img_inicio
    try:
        imagen_original = Image.open("Image.png")
    except Exception:
        img_inicio = None
        return None

    parent.update_idletasks()
    available_w = parent.winfo_width()
    available_h = parent.winfo_height()
    if available_w > 1:
        max_w = max(150, available_w - 40)
    if available_h > 1:
        max_h = max(120, available_h - 20)

    ancho, alto = imagen_original.size
    factor = min(max_w / ancho, max_h / alto, 1)
    nuevo_ancho = max(1, int(ancho * factor))
    nuevo_alto = max(1, int(alto * factor))

    imagen_redimensionada = imagen_original.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
    img = ImageTk.PhotoImage(imagen_redimensionada)
    img_inicio = img
    return img
