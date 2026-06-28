"""Widgets y helpers de UI reutilizables (botones, entradas, autocompletado, imagen de inicio)."""
import math
import tkinter as tk

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
        relief="ridge"
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


def cargar_imagen_inicio(parent, max_w=820, max_h=580):
    global img_inicio
    try:
        img = tk.PhotoImage(file="Image.png")
    except Exception:
        img_inicio = None
        return None

    parent.update_idletasks()
    available_w = parent.winfo_width()
    available_h = parent.winfo_height()
    if available_w > 1:
        max_w = min(max_w, max(200, available_w - 40))
    if available_h > 1:
        max_h = min(max_h, max(160, available_h // 2))

    factor = max(1, math.ceil(max(img.width() / max_w, img.height() / max_h)))
    if factor > 1:
        img = img.subsample(factor, factor)
    img_inicio = img
    return img
