"""Exportacion de datos a Google Sheets."""
import logging
import threading
import time
from decimal import Decimal
from datetime import datetime, date

import gspread
from google.oauth2.service_account import Credentials

from config import GOOGLE_CREDS_FILE, GOOGLE_SCOPES, SPREADSHEET_NAME
from db import cursor, DB_PATH
import sqlite3

SHEETS_HABILITADO = False
client = None

try:
    creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=GOOGLE_SCOPES)
    client = gspread.authorize(creds)
    SHEETS_HABILITADO = True
except Exception:
    SHEETS_HABILITADO = False

# Evita exportaciones simultaneas (mas seguro y eficiente).
EXPORT_LOCK = threading.Lock()
EXPORT_RUNNING = threading.Event()


def exportar_a_sheet(nombre_hoja, encabezados, filas, sort_col=None):
    filas_convertidas = [
        [
            float(x) if isinstance(x, Decimal)
            else x.strftime("%Y-%m-%d %H:%M:%S") if isinstance(x, datetime)
            else x.strftime("%Y-%m-%d") if isinstance(x, date)
            else x
            for x in fila
        ]
        for fila in filas
    ]

    sheet = client.open(SPREADSHEET_NAME).worksheet(nombre_hoja)
    sheet.clear()
    sheet.append_row(encabezados)

    bloque = 50
    for i in range(0, len(filas_convertidas), bloque):
        sheet.append_rows(filas_convertidas[i:i + bloque])
        time.sleep(1)  # pausa entre cada bloque para no exceder cuota de la API

    if sort_col and filas_convertidas:
        # Ordenar datos (sin tocar encabezados) por la columna solicitada
        sheet.spreadsheet.batch_update({
            "requests": [
                {
                    "sortRange": {
                        "range": {
                            "sheetId": sheet.id,
                            "startRowIndex": 1,
                            "endRowIndex": 1 + len(filas_convertidas),
                            "startColumnIndex": 0,
                            "endColumnIndex": len(encabezados),
                        },
                        "sortSpecs": [
                            {
                                "dimensionIndex": sort_col - 1,
                                "sortOrder": "ASCENDING",
                            }
                        ],
                    }
                }
            ]
        })


def exportar_ventas(cur=cursor):
    cur.execute("""
        SELECT v.id, d.nombre_perfume, d.cantidad, d.tipo_precio,
               d.total, v.metodo_pago, v.fecha
        FROM ventas v
        JOIN detalle_venta d ON v.id = d.venta_id
    """)
    filas = cur.fetchall()
    encabezados = ["ID Venta", "Perfume", "Cantidad", "Tipo Precio", "Total", "Metodo Pago", "Fecha"]
    exportar_a_sheet("Ventas", encabezados, filas)


def exportar_inventario(cur=cursor):
    cur.execute("""
        SELECT
            i.id,
            i.marca,
            i.nombre,
            i.precio,
            i.precio_mayoreo,
            i.existencias
        FROM inventario i
        ORDER BY TRIM(i.marca) COLLATE NOCASE ASC, TRIM(i.nombre) COLLATE NOCASE ASC
    """)
    filas = cur.fetchall()
    encabezados = ["ID", "Marca", "Perfume", "Precio", "Precio Mayoreo", "Existencias"]
    exportar_a_sheet("Inventario", encabezados, filas, sort_col=2)


def exportar_proveedores(cur=cursor):
    cur.execute("SELECT id, nombre, telefono FROM proveedores")
    filas = cur.fetchall()
    encabezados = ["ID", "Proveedor", "Telefono"]
    exportar_a_sheet("Proveedores", encabezados, filas)


def exportar_economia(cur=cursor):
    cur.execute("""
        SELECT DATE(v.fecha), SUM(d.total), SUM(d.ganancia)
        FROM ventas v
        JOIN detalle_venta d ON v.id=d.venta_id
        WHERE v.metodo_pago != 'Regalo'
        GROUP BY DATE(v.fecha)
    """)
    filas = cur.fetchall()
    encabezados = ["Fecha", "Total Vendido", "Ganancia"]
    exportar_a_sheet("Economia", encabezados, filas)


def exportar_clientes(cur=cursor):
    cur.execute("""
        SELECT c.id, c.nombre, c.telefono, c.correo, c.tipo,
               IFNULL(SUM(d.total),0)
        FROM clientes c
        LEFT JOIN ventas v ON c.id = v.cliente_id
        LEFT JOIN detalle_venta d ON v.id = d.venta_id
        GROUP BY c.id
    """)
    filas = cur.fetchall()
    encabezados = ["ID", "Nombre", "Telefono", "Correo", "Tipo", "Total Comprado"]
    exportar_a_sheet("Clientes", encabezados, filas)


def exportar_todo():
    if not SHEETS_HABILITADO:
        return

    with EXPORT_LOCK:
        if EXPORT_RUNNING.is_set():
            return
        EXPORT_RUNNING.set()

    conexion_hilo = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor_hilo = conexion_hilo.cursor()

    try:
        exportar_ventas(cursor_hilo)
        exportar_inventario(cursor_hilo)
        exportar_proveedores(cursor_hilo)
        exportar_clientes(cursor_hilo)
        exportar_economia(cursor_hilo)
    except Exception:
        logging.exception("Error al sincronizar con Google Sheets")
    finally:
        cursor_hilo.close()
        conexion_hilo.close()
        EXPORT_RUNNING.clear()


def exportar_todo_async():
    threading.Thread(target=exportar_todo, daemon=True).start()
