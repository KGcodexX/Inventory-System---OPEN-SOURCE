import auth
from db import cursor


def test_hay_usuarios_es_falso_si_no_existe_ninguno():
    assert auth.hay_usuarios() is False


def test_crear_usuario_y_verificar_credenciales_correctas():
    auth.crear_usuario("mama", "clave1234", "admin")

    assert auth.hay_usuarios() is True
    assert auth.verificar_credenciales("mama", "clave1234") == "admin"


def test_verificar_credenciales_con_password_incorrecta_retorna_none():
    auth.crear_usuario("mama", "clave1234", "admin")

    assert auth.verificar_credenciales("mama", "otra_clave") is None


def test_verificar_credenciales_con_usuario_inexistente_retorna_none():
    assert auth.verificar_credenciales("nadie", "loquesea") is None


def test_password_no_se_guarda_en_texto_plano():
    auth.crear_usuario("mama", "clave1234", "admin")

    cursor.execute("SELECT password_hash FROM usuarios WHERE usuario=?", ("mama",))
    password_hash = cursor.fetchone()[0]

    assert password_hash != "clave1234"


def test_dos_usuarios_con_la_misma_password_tienen_hashes_distintos():
    auth.crear_usuario("mama", "clave1234", "admin")
    auth.crear_usuario("empleada", "clave1234", "vendedora")

    cursor.execute("SELECT password_hash, password_salt FROM usuarios WHERE usuario=?", ("mama",))
    hash_mama, salt_mama = cursor.fetchone()

    cursor.execute("SELECT password_hash, password_salt FROM usuarios WHERE usuario=?", ("empleada",))
    hash_empleada, salt_empleada = cursor.fetchone()

    assert salt_mama != salt_empleada
    assert hash_mama != hash_empleada


def test_crear_usuario_con_rol_invalido_lanza_error():
    try:
        auth.crear_usuario("mama", "clave1234", "rol_que_no_existe")
        assert False, "deberia haber lanzado ValueError"
    except ValueError:
        pass


def test_es_admin_segun_el_rol_de_la_sesion_activa():
    auth.crear_usuario("mama", "clave1234", "admin")
    auth.crear_usuario("empleada", "clave1234", "vendedora")

    auth.iniciar_sesion("mama", "admin")
    assert auth.es_admin() is True

    auth.iniciar_sesion("empleada", "vendedora")
    assert auth.es_admin() is False


def test_es_admin_es_falso_sin_sesion_iniciada():
    assert auth.es_admin() is False


def test_cerrar_sesion_limpia_la_sesion_actual():
    auth.crear_usuario("mama", "clave1234", "admin")
    auth.iniciar_sesion("mama", "admin")

    auth.cerrar_sesion()

    assert auth.sesion_actual is None
    assert auth.es_admin() is False
