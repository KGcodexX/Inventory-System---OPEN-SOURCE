"""Configuracion de estilos ttk y opciones globales de Tk."""
from tkinter import ttk

from config import (
    BG_COLOR, BTN_BG, BTN_FG, BTN_HOVER, CARD_BG, FONT, FONT_BOLD,
    TEXT_COLOR, TREE_BG, TREE_SEL,
)


def configurar_opciones_globales(root):
    root.option_add("*Background", BG_COLOR)
    root.option_add("*Foreground", TEXT_COLOR)
    root.option_add("*Button.Background", BTN_BG)
    root.option_add("*Button.Foreground", BTN_FG)
    root.option_add("*Button.ActiveBackground", BTN_HOVER)
    root.option_add("*Button.ActiveForeground", BTN_FG)
    root.option_add("*Entry.Background", CARD_BG)
    root.option_add("*Entry.Foreground", TEXT_COLOR)
    root.option_add("*Entry.InsertBackground", TEXT_COLOR)
    root.option_add("*Entry.BorderWidth", 0)
    root.option_add("*Entry.Relief", "flat")
    root.option_add("*Entry.HighlightThickness", 0)
    root.option_add("*Label.Background", BG_COLOR)
    root.option_add("*Label.Foreground", TEXT_COLOR)
    root.option_add("*Toplevel.Background", BG_COLOR)
    root.option_add("*TCombobox*Listbox*Background", CARD_BG)
    root.option_add("*TCombobox*Listbox*Foreground", TEXT_COLOR)
    root.option_add("*TCombobox*Listbox*selectBackground", TREE_SEL)
    root.option_add("*TCombobox*Listbox*selectForeground", TEXT_COLOR)


def configurar_estilos(style: ttk.Style):
    style.theme_use("clam")

    style.configure("Treeview",
                    background=TREE_BG,
                    foreground=TEXT_COLOR,
                    fieldbackground=TREE_BG,
                    font=FONT,
                    rowheight=25,
                    bordercolor=BG_COLOR,
                    borderwidth=0)
    style.configure("Treeview.Heading",
                    background=BTN_BG,
                    foreground=BTN_FG,
                    font=FONT_BOLD,
                    relief="flat")
    style.map("Treeview",
              background=[('selected', TREE_SEL)],
              foreground=[('selected', 'white')])

    style.configure("Dark.TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=FONT)

    style.configure(
        "TCombobox",
        fieldbackground=CARD_BG,
        background=CARD_BG,
        foreground=TEXT_COLOR,
        arrowcolor=TEXT_COLOR,
        borderwidth=0,
        relief="flat"
    )
    style.map(
        "TCombobox",
        bordercolor=[("focus", CARD_BG), ("!focus", CARD_BG)],
        lightcolor=[("focus", CARD_BG), ("!focus", CARD_BG)],
        darkcolor=[("focus", CARD_BG), ("!focus", CARD_BG)]
    )

    style.configure(
        "Pago.TCombobox",
        fieldbackground=CARD_BG,
        background=CARD_BG,
        foreground=TEXT_COLOR,
        arrowcolor=TEXT_COLOR
    )
    style.map(
        "Pago.TCombobox",
        fieldbackground=[("readonly", CARD_BG)],
        foreground=[("readonly", TEXT_COLOR)]
    )

    style.configure(
        "Precio.TCombobox",
        fieldbackground=CARD_BG,
        background=CARD_BG,
        foreground=TEXT_COLOR,
        arrowcolor=TEXT_COLOR
    )
    style.map(
        "Precio.TCombobox",
        fieldbackground=[("readonly", CARD_BG)],
        foreground=[("readonly", TEXT_COLOR)]
    )
