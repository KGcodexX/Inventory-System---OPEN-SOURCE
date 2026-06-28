"""Constantes globales: colores, fuentes y configuracion de entorno."""
import os

# ---------------- COLORES Y FUENTES ----------------
BG_COLOR = "#0f0f0f"
FRAME_MENU_BG = "#151515"
BTN_BG = "#2b2b2b"
BTN_HOVER = "#3a3a3a"
BTN_FG = "#f2f2f2"
TEXT_COLOR = "#e6e6e6"
CARD_BG = "#1a1a1a"
TREE_BG = "#1a1a1a"
TREE_ALT = "#222222"
TREE_SEL = "#4a4a4a"
ACCENT_COLOR = "#d4af37"
ALERTA_COLOR = "#c0392b"

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 9)

BTN_WIDTH = 14
BTN_PADX = 4
BTN_PADY = 4

# ---------------- BASE DE DATOS Y GOOGLE SHEETS ----------------
DB_PATH = os.getenv("PERFUMERIA_DB_PATH", "perfumeria.db")
GOOGLE_CREDS_FILE = os.getenv("PERFUMERIA_GOOGLE_CREDS", "credenciales.json")
SPREADSHEET_NAME = os.getenv("PERFUMERIA_SHEET_NAME", "PERFUMES")

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ---------------- INVENTARIO Y PREDICCION ----------------
UMBRAL_STOCK_BAJO = int(os.getenv("PERFUMERIA_UMBRAL_STOCK_BAJO", "5"))
DIAS_VELOCIDAD_VENTA = 30
