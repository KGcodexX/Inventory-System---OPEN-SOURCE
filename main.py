"""Punto de entrada del Sistema de Perfumeria."""
import logging
from tkinter import messagebox

from app import crear_ventana_principal
from db import crear_tablas, respaldar_base_datos
from login import mostrar_login
from registro import configurar_logging


def manejar_excepcion_tk(exc_type, exc_value, exc_traceback):
    logging.error("Error no controlado en la interfaz", exc_info=(exc_type, exc_value, exc_traceback))
    messagebox.showerror(
        "Error inesperado",
        f"Ocurrio un error inesperado:\n{exc_value}\n\nSe guardo el detalle en logs/app.log"
    )


def main():
    configurar_logging()
    logging.info("Iniciando aplicacion")

    try:
        crear_tablas()
        respaldar_base_datos()

        if not mostrar_login():
            logging.info("Login cancelado, cerrando aplicacion")
            return

        root = crear_ventana_principal()
        root.report_callback_exception = manejar_excepcion_tk
        root.mainloop()
    except Exception:
        logging.exception("Error fatal al iniciar la aplicacion")
        raise


if __name__ == "__main__":
    main()
