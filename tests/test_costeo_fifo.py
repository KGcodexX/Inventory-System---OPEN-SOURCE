from db import cursor

from ventas import (
    aplicar_descuento_lotes,
    calcular_costo_estimado,
    revertir_descuento_lotes,
)


def obtener_disponibles(perfume_id):
    cursor.execute("""
        SELECT unidades_disponibles FROM lote_inventario
        WHERE perfume_id = ?
        ORDER BY fecha_compra ASC
    """, (perfume_id,))
    return [row[0] for row in cursor.fetchall()]


def test_calcular_costo_estimado_usa_orden_fifo(perfume_con_dos_lotes):
    perfume_id = perfume_con_dos_lotes

    costo = calcular_costo_estimado(perfume_id, 7)

    assert costo == 5 * 10 + 2 * 20
    assert obtener_disponibles(perfume_id) == [5, 5]


def test_calcular_costo_estimado_no_modifica_la_base(perfume_con_dos_lotes):
    perfume_id = perfume_con_dos_lotes

    calcular_costo_estimado(perfume_id, 3)
    calcular_costo_estimado(perfume_id, 3)
    calcular_costo_estimado(perfume_id, 3)

    assert obtener_disponibles(perfume_id) == [5, 5]


def test_aplicar_descuento_lotes_consume_el_lote_mas_antiguo_primero(perfume_con_dos_lotes):
    perfume_id = perfume_con_dos_lotes

    costo = aplicar_descuento_lotes(perfume_id, 7)

    assert costo == 5 * 10 + 2 * 20
    assert obtener_disponibles(perfume_id) == [0, 3]


def test_aplicar_descuento_lotes_no_pasa_de_lo_disponible(perfume_con_dos_lotes):
    perfume_id = perfume_con_dos_lotes

    aplicar_descuento_lotes(perfume_id, 10)

    assert obtener_disponibles(perfume_id) == [0, 0]


def test_revertir_descuento_lotes_restaura_unidades_consumidas(perfume_con_dos_lotes):
    perfume_id = perfume_con_dos_lotes

    aplicar_descuento_lotes(perfume_id, 7)
    revertir_descuento_lotes(perfume_id, 7)

    assert obtener_disponibles(perfume_id) == [5, 5]


def test_revertir_descuento_lotes_no_excede_la_cantidad_original(perfume_con_dos_lotes):
    perfume_id = perfume_con_dos_lotes

    aplicar_descuento_lotes(perfume_id, 7)
    revertir_descuento_lotes(perfume_id, 100)

    assert obtener_disponibles(perfume_id) == [5, 5]


def test_venta_y_eliminacion_dejan_los_lotes_como_estaban(perfume_con_dos_lotes):
    perfume_id = perfume_con_dos_lotes

    costo_venta_1 = aplicar_descuento_lotes(perfume_id, 4)
    costo_venta_2 = aplicar_descuento_lotes(perfume_id, 3)

    assert obtener_disponibles(perfume_id) == [0, 3]

    revertir_descuento_lotes(perfume_id, 3)
    revertir_descuento_lotes(perfume_id, 4)

    assert obtener_disponibles(perfume_id) == [5, 5]
    assert costo_venta_1 + costo_venta_2 == 5 * 10 + 2 * 20
