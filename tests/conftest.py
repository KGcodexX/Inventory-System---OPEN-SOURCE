import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["PERFUMERIA_DB_PATH"] = ":memory:"

import pytest

import auth
from db import conexion, crear_tablas, cursor

crear_tablas()


@pytest.fixture(autouse=True)
def limpiar_tablas():
    cursor.execute("DELETE FROM lote_inventario")
    cursor.execute("DELETE FROM detalle_venta")
    cursor.execute("DELETE FROM ventas")
    cursor.execute("DELETE FROM detalle_compra")
    cursor.execute("DELETE FROM compras")
    cursor.execute("DELETE FROM inventario")
    cursor.execute("DELETE FROM clientes")
    cursor.execute("DELETE FROM proveedores")
    cursor.execute("DELETE FROM usuarios")
    conexion.commit()
    auth.cerrar_sesion()
    yield


@pytest.fixture
def perfume_con_dos_lotes():
    cursor.execute("""
        INSERT INTO inventario (marca, sexo, nombre, mililitros, precio, precio_mayoreo, existencias)
        VALUES ('Marca', 'Unisex', 'Perfume Test', 100, 500, 400, 10)
    """)
    perfume_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO lote_inventario (perfume_id, cantidad, unidades_disponibles, costo_unitario, fecha_compra)
        VALUES (?, 5, 5, 10, '2026-01-01 00:00:00')
    """, (perfume_id,))

    cursor.execute("""
        INSERT INTO lote_inventario (perfume_id, cantidad, unidades_disponibles, costo_unitario, fecha_compra)
        VALUES (?, 5, 5, 20, '2026-02-01 00:00:00')
    """, (perfume_id,))

    conexion.commit()
    return perfume_id
