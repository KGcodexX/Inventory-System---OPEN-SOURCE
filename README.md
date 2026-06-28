# Sistema de Perfumería

Aplicación de escritorio desarrollada para administrar el funcionamiento diario de un negocio de venta de perfumes. Actualmente se utiliza en un negocio real para gestionar inventario, ventas, clientes, proveedores y el control financiero desde una sola aplicación.

## ¿Por qué se desarrolló?

Antes de implementar este sistema, toda la información se llevaba de forma manual. Esto ocasionaba errores frecuentes al calcular las ganancias reales, especialmente porque un mismo perfume podía comprarse en diferentes fechas y a distintos costos. Además, obtener información como el inventario disponible, los clientes más frecuentes o las ventas del día requería revisar los registros manualmente.

El objetivo del proyecto fue automatizar estos procesos y facilitar la administración del negocio mediante una herramienta sencilla y rápida de utilizar.

---

# Funcionalidades

### Inicio de sesión y control de usuarios

El sistema cuenta con autenticación mediante usuario y contraseña, además de dos niveles de acceso:

* **Administrador**, con acceso completo al sistema.
* **Vendedora**, enfocada únicamente en las operaciones del día a día, sin permisos para modificar precios o eliminar información.

Las contraseñas se almacenan utilizando **hash + salt**, evitando guardarlas en texto plano.

---

### Inventario

Permite registrar, modificar y eliminar perfumes, además de realizar búsquedas rápidas por nombre para localizar productos fácilmente.

---

### Ventas

Cada venta registra:

* método de pago;
* tipo de precio (normal, mayoreo o personalizado);
* cantidad vendida;
* costo real del producto utilizando costeo FIFO.

Esto permite conocer con precisión la utilidad obtenida en cada venta.

---

### Clientes

El sistema permite registrar clientes y consultar su historial completo de compras, facilitando el seguimiento de clientes frecuentes.

---

### Proveedores

Las compras realizadas a proveedores generan automáticamente nuevos lotes de inventario con su costo correspondiente, información que posteriormente utiliza el sistema para calcular correctamente las ganancias.

---

### Economía

Incluye un módulo con indicadores importantes para el negocio, como:

* ventas del día y del mes;
* ganancias;
* perfumes más vendidos;
* perfumes con menor rotación;
* clientes con mayor volumen de compras.

---

### Recibos en PDF

Desde el módulo de ventas es posible generar un recibo en formato PDF con toda la información de la compra, incluyendo productos, marca, cantidad, tipo de precio y total.

---

### Sincronización con Google Sheets (opcional)

De manera opcional, el sistema puede sincronizar automáticamente la información con una hoja de cálculo de Google Sheets.

Esta sincronización se realiza en segundo plano para evitar que la interfaz se bloquee mientras se envían los datos. Si no se configura, la aplicación continúa funcionando normalmente utilizando únicamente la base de datos local.

---

### Respaldos automáticos

Antes de realizar operaciones que eliminan información y cada vez que inicia la aplicación, se crea automáticamente una copia de seguridad de la base de datos dentro de la carpeta `backups/`.

---

### Registro de errores

Los errores inesperados se almacenan en `logs/app.log`, facilitando el diagnóstico y la corrección de problemas sin perder información importante.

---

# Arquitectura del proyecto

El proyecto está organizado por módulos, donde cada archivo tiene una responsabilidad específica.

| Archivo                                                                      | Función                                                           |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `main.py`                                                                    | Punto de entrada y manejo de excepciones generales.               |
| `app.py`                                                                     | Ventana principal y navegación de la aplicación.                  |
| `config.py`                                                                  | Configuración de colores, fuentes y constantes.                   |
| `db.py`                                                                      | Base de datos SQLite, creación de tablas y respaldos automáticos. |
| `auth.py`                                                                    | Autenticación y control de permisos.                              |
| `login.py`                                                                   | Inicio de sesión y creación del primer administrador.             |
| `usuarios.py`                                                                | Administración de usuarios.                                       |
| `recibos.py`                                                                 | Generación de recibos PDF.                                        |
| `registro.py`                                                                | Configuración del sistema de logs.                                |
| `sheets.py`                                                                  | Sincronización con Google Sheets.                                 |
| `styles.py`                                                                  | Personalización de estilos `ttk`.                                 |
| `widgets.py`                                                                 | Componentes reutilizables de la interfaz.                         |
| `inventario.py`, `clientes.py`, `ventas.py`, `economia.py`, `proveedores.py` | Pantallas principales del sistema.                                |
| `tests/`                                                                     | Pruebas automatizadas.                                            |

---

# Costeo FIFO

El sistema utiliza el método **FIFO (First In, First Out)** para calcular el costo real de cada venta.

Cada compra realizada a un proveedor genera un nuevo lote con su propio costo unitario. Cuando se vende un perfume, el sistema consume primero las unidades pertenecientes a los lotes más antiguos, permitiendo obtener una utilidad mucho más precisa que utilizando un costo promedio.

---

# Problema técnico resuelto

Durante el desarrollo se detectó un problema importante en la lógica de ventas.

Originalmente, el descuento del inventario se realizaba cuando el usuario agregaba un perfume a la lista temporal de una venta. Si posteriormente cancelaba la operación, el inventario ya había sido modificado aunque la venta nunca se registrara.

Esto provocaba inconsistencias entre el inventario y las ventas almacenadas.

La solución consistió en dividir el proceso en dos etapas:

* `calcular_costo_estimado()`: calcula el costo utilizando FIFO únicamente para mostrar una vista previa, sin modificar la base de datos.
* `aplicar_descuento_lotes()`: descuenta definitivamente las unidades únicamente cuando la venta es confirmada.

Además, se implementó `revertir_descuento_lotes()`, encargado de restaurar las unidades consumidas cuando una venta es eliminada, manteniendo la consistencia del inventario.

También se corrigieron otros problemas importantes, entre ellos:

* evitar que una misma venta permitiera agregar más unidades de las disponibles cuando un producto se añadía varias veces;
* mejorar la validación de formularios para impedir cierres inesperados causados por datos inválidos o campos vacíos.

---

# Pruebas automatizadas

El proyecto incluye pruebas automatizadas para verificar:

* la lógica del costeo FIFO;
* la autenticación de usuarios.

Las pruebas utilizan una base de datos SQLite en memoria para no afectar los datos reales y se ejecutan automáticamente mediante GitHub Actions en cada actualización del repositorio.

Para ejecutarlas localmente:

```bash
pip install pytest
python -m pytest tests/ -v
```

---

# Tecnologías utilizadas

* Python 3
* Tkinter / ttk
* SQLite
* gspread
* Google Service Account
* fpdf2

---

# Ejecución del proyecto

```bash
pip install -r requirements.txt
python main.py
```

La aplicación utiliza `Image.png` como imagen de bienvenida. Si el archivo no está presente, el sistema continúa funcionando sin inconvenientes.

El archivo `credenciales.json` únicamente es necesario si se desea habilitar la sincronización con Google Sheets.

---

# Configuración de Google Sheets (opcional)

Para habilitar la sincronización:

1. Crear un proyecto en Google Cloud Console.
2. Activar las APIs de Google Sheets y Google Drive.
3. Crear una Service Account.
4. Descargar el archivo JSON de credenciales.
5. Renombrarlo como `credenciales.json`.
6. Colocarlo junto a `main.py`.
7. Compartir la hoja de cálculo con el correo de la cuenta de servicio otorgándole permisos de edición.

Si las credenciales no existen o son incorrectas, la aplicación simplemente continuará funcionando utilizando la base de datos local.
