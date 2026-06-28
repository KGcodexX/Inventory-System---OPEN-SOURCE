# Changelog

Todos los cambios importantes del proyecto se anotan aquí.

## [1.1.0] - 2026-06-27

Esta vuelta fue más sobre hacer la app útil para tomar decisiones, no solo para registrar datos.

Agregado:
- Alerta de stock bajo, configurable, con aviso al iniciar sesión (y un botón en Inicio para apagarla si molesta).
- Estimación de cuántos días le quedan a cada perfume antes de agotarse, basada en su ritmo de venta de los últimos 30 días.
- Filtro por rango de fechas en el historial de ventas (antes solo se podía buscar por cliente).
- Gráfica de los perfumes que más dinero generan, dentro de Economía.
- Botón para exportar el resumen de Economía completo a PDF.
- Pantalla de inicio con tarjetas de resumen (ventas, total, ganancia y stock bajo del día).

Cambiado:
- Botones más grandes en todo el sistema, con cursor de mano al pasar el mouse.
- La imagen de bienvenida ya no se distorsiona ni se ve pixeleada al cambiar el tamaño de la ventana (se usa Pillow en vez del escalado básico de Tkinter).
- Scroll con la rueda del mouse en la pantalla de Economía.
- Se quitaron los iconos del menú lateral, quedó más limpio sin ellos.

## [1.0.0] - 2026-06-27

Primera versión "de verdad" del sistema. Antes de esto era un solo archivo de más de 1000 líneas; aquí quedó dividido en módulos y con los problemas más graves resueltos.

Agregado:
- Inicio de sesión con dos roles (admin y vendedora), contraseñas con hash + salt.
- Generación de recibos de venta en PDF.
- Respaldo automático de la base de datos antes de operaciones que borran información, y al iniciar la app.
- Registro de errores a archivo (`logs/app.log`).
- Pruebas automatizadas para el costeo FIFO y la autenticación, corriendo en CI con GitHub Actions.
- Sincronización opcional con Google Sheets (la app ya no truena si no hay credenciales configuradas).

Corregido:
- El bug más importante de este proyecto: el sistema descontaba el inventario de los lotes FIFO en cuanto se agregaba un perfume a una venta en proceso, no cuando se confirmaba. Si alguien cancelaba a mitad de camino, el inventario quedaba mal sin que existiera ninguna venta registrada. Se separó en dos pasos: calcular el costo (sin tocar nada) y aplicarlo de verdad (solo al guardar).
- Se podía vender más unidades de las que había en existencia si el mismo perfume se agregaba dos veces a una venta antes de guardarla.
- Las ventanas de formularios se cerraban de golpe si dejabas un campo vacío o escribías texto donde se esperaba un número.

---

Antes de la v1.0.0 el proyecto era un script único sin control de versiones, así que no hay un registro formal de esa etapa.
