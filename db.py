"""Conexion a SQLite, creacion de tablas y respaldos."""
import os
import shutil
import sqlite3
from datetime import datetime

from config import DB_PATH

conexion = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conexion.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

BACKUPS_DIR = "backups"
MAX_BACKUPS = 20


def respaldar_base_datos():
    if DB_PATH == ":memory:" or not os.path.exists(DB_PATH):
        return

    os.makedirs(BACKUPS_DIR, exist_ok=True)
    conexion.commit()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(BACKUPS_DIR, f"perfumeria_{timestamp}.db")
    shutil.copy2(DB_PATH, destino)

    _limpiar_backups_viejos()


def _limpiar_backups_viejos():
    archivos = sorted(
        f for f in os.listdir(BACKUPS_DIR)
        if f.startswith("perfumeria_") and f.endswith(".db")
    )
    exceso = len(archivos) - MAX_BACKUPS
    for nombre in archivos[:max(0, exceso)]:
        os.remove(os.path.join(BACKUPS_DIR, nombre))


def crear_tablas():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT,
            sexo TEXT,
            nombre TEXT,
            mililitros REAL,
            precio REAL,
            precio_mayoreo REAL,
            existencias INTEGER,
            costo_actual REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            correo TEXT,
            tipo TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            correo TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            metodo_pago TEXT,
            fecha TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            perfume_id INTEGER,
            nombre_perfume TEXT,
            cantidad INTEGER,
            tipo_precio TEXT,
            total REAL,
            costo_unitario REAL,
            ganancia REAL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (perfume_id) REFERENCES inventario(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor_id INTEGER,
            total REAL,
            fecha TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compra_id INTEGER,
            perfume_id INTEGER,
            cantidad INTEGER,
            costo_unitario REAL,
            total REAL,
            FOREIGN KEY (compra_id) REFERENCES compras(id),
            FOREIGN KEY (perfume_id) REFERENCES inventario(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lote_inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            perfume_id INTEGER,
            cantidad INTEGER,
            unidades_disponibles INTEGER,
            costo_unitario REAL,
            fecha_compra TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (perfume_id) REFERENCES inventario(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            password_hash TEXT,
            password_salt TEXT,
            rol TEXT
        )
    """)
    conexion.commit()


def resecuenciar_ids_inventario():
    """Recalcula los IDs de inventario para que sean consecutivos sin huecos."""
    cursor.execute("SELECT id FROM inventario ORDER BY id")
    ids = [row[0] for row in cursor.fetchall()]
    if not ids:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='inventario'")
        return

    mapping = {old_id: new_id for new_id, old_id in enumerate(ids, start=1)}
    if all(old_id == new_id for old_id, new_id in mapping.items()):
        return

    offset = 1000000
    cursor.execute("PRAGMA foreign_keys = OFF")
    try:
        for old_id, new_id in mapping.items():
            if old_id == new_id:
                continue
            tmp_id = old_id + offset
            cursor.execute("UPDATE inventario SET id=? WHERE id=?", (tmp_id, old_id))
            cursor.execute("UPDATE detalle_venta SET perfume_id=? WHERE perfume_id=?", (tmp_id, old_id))
            cursor.execute("UPDATE detalle_compra SET perfume_id=? WHERE perfume_id=?", (tmp_id, old_id))
            cursor.execute("UPDATE lote_inventario SET perfume_id=? WHERE perfume_id=?", (tmp_id, old_id))

        for old_id, new_id in mapping.items():
            if old_id == new_id:
                continue
            tmp_id = old_id + offset
            cursor.execute("UPDATE inventario SET id=? WHERE id=?", (new_id, tmp_id))
            cursor.execute("UPDATE detalle_venta SET perfume_id=? WHERE perfume_id=?", (new_id, tmp_id))
            cursor.execute("UPDATE detalle_compra SET perfume_id=? WHERE perfume_id=?", (new_id, tmp_id))
            cursor.execute("UPDATE lote_inventario SET perfume_id=? WHERE perfume_id=?", (new_id, tmp_id))

        cursor.execute(
            "INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES ('inventario', ?)",
            (len(ids),)
        )
    finally:
        cursor.execute("PRAGMA foreign_keys = ON")
