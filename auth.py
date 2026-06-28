"""Autenticacion de usuarios y control de roles (admin / vendedora)."""
import hashlib
import os

from db import conexion, cursor

ROLES = ("admin", "vendedora")

sesion_actual = None


def _hashear_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    hash_resultado = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()
    return hash_resultado, salt


def hay_usuarios():
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    return cursor.fetchone()[0] > 0


def crear_usuario(usuario, password, rol):
    if rol not in ROLES:
        raise ValueError(f"Rol invalido: {rol}")

    password_hash, salt = _hashear_password(password)
    cursor.execute(
        "INSERT INTO usuarios (usuario, password_hash, password_salt, rol) VALUES (?,?,?,?)",
        (usuario, password_hash, salt, rol)
    )
    conexion.commit()


def verificar_credenciales(usuario, password):
    cursor.execute("SELECT password_hash, password_salt, rol FROM usuarios WHERE usuario=?", (usuario,))
    fila = cursor.fetchone()
    if not fila:
        return None

    password_hash_guardado, salt, rol = fila
    password_hash_ingresado, _ = _hashear_password(password, salt)

    if password_hash_ingresado != password_hash_guardado:
        return None

    return rol


def iniciar_sesion(usuario, rol):
    global sesion_actual
    sesion_actual = {"usuario": usuario, "rol": rol}


def cerrar_sesion():
    global sesion_actual
    sesion_actual = None


def es_admin():
    return sesion_actual is not None and sesion_actual["rol"] == "admin"
