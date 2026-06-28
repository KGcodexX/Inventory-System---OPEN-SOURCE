"""Preferencias persistentes de la aplicacion (no ligadas a un usuario especifico)."""
import json
import os

PREFERENCIAS_FILE = "preferencias.json"

_predeterminadas = {
    "notificaciones_stock_bajo": True,
}


def _cargar():
    if not os.path.exists(PREFERENCIAS_FILE):
        return dict(_predeterminadas)
    try:
        with open(PREFERENCIAS_FILE, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except Exception:
        return dict(_predeterminadas)
    return {**_predeterminadas, **datos}


def _guardar(datos):
    with open(PREFERENCIAS_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2)


def notificaciones_activas():
    return _cargar().get("notificaciones_stock_bajo", True)


def alternar_notificaciones():
    datos = _cargar()
    datos["notificaciones_stock_bajo"] = not datos.get("notificaciones_stock_bajo", True)
    _guardar(datos)
    return datos["notificaciones_stock_bajo"]
