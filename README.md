# Sistema de Perfumeria

Aplicacion de escritorio para gestionar inventario, ventas, clientes, proveedores y economia de un negocio real de venta de perfumes. Esta en uso activo por una proveedora de perfumes para llevar su operacion diaria.

## Por que existe

Antes de esta app, el control de inventario, ventas y costos se llevaba de forma manual. Eso generaba dos problemas concretos: errores al calcular cuanto costaba realmente cada perfume vendido (porque el mismo perfume se compraba en distintos lotes a distintos costos), y falta de visibilidad rapida sobre ganancias, clientes top y stock bajo.

## Que hace

- **Inicio de sesion con roles**: cuenta de administrador (acceso total) y cuentas de vendedora (operacion diaria, sin permisos para eliminar o editar precios).
- **Inventario**: alta, edicion y baja de perfumes, con busqueda por nombre.
- **Ventas**: registro de ventas con metodo de pago, tipo de precio (normal, mayoreo, personalizado) y calculo de costo real por venta.
- **Recibos en PDF**: genera un recibo descargable de cualquier venta, con perfume, marca, cantidad, tipo de precio y total.
- **Clientes**: alta de clientes y consulta de su historial de compras.
- **Proveedores y pedidos**: registro de compras a proveedores, que alimentan el inventario y los lotes de costo.
- **Economia**: resumen de ventas y ganancias del dia/mes, top de perfumes y clientes, perfumes menos vendidos.
- **Sincronizacion con Google Sheets (opcional)**: cada operacion exporta automaticamente los datos a una hoja de calculo en segundo plano, sin bloquear la interfaz. Si no se configura, la app funciona igual solo con la base de datos local.
- **Respaldos automaticos**: antes de cada operacion destructiva (eliminar perfume, cliente o venta) y al iniciar la app, se guarda una copia de la base de datos en `backups/`.
- **Registro de errores**: los errores inesperados quedan guardados en `logs/app.log` para poder diagnosticarlos despues, en vez de perderse en silencio.

## Arquitectura

El proyecto esta dividido por responsabilidad

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Punto de entrada, manejo de excepciones no controladas |
| `app.py` | Ventana principal, menu lateral, pantalla de inicio |
| `config.py` | Colores, fuentes y constantes de entorno |
| `db.py` | Conexion SQLite, esquema de tablas y respaldos automaticos |
| `auth.py` | Autenticacion de usuarios y control de roles (admin / vendedora) |
| `login.py` | Pantalla de inicio de sesion y creacion de la primera cuenta admin |
| `usuarios.py` | Gestion de usuarios (solo administradores) |
| `recibos.py` | Generacion de recibos de venta en PDF |
| `registro.py` | Configuracion de logging de errores a archivo |
| `sheets.py` | Exportacion a Google Sheets (en hilo separado, opcional) |
| `styles.py` | Estilos `ttk` (Treeview, Combobox) |
| `widgets.py` | Componentes de UI reutilizables |
| `inventario.py`, `clientes.py`, `ventas.py`, `economia.py`, `proveedores.py` | Una pantalla por archivo, con su propio estado |
| `tests/` | Tests automatizados (costeo FIFO y autenticacion), corren en CI con GitHub Actions |

El costeo de inventario usa un metodo **FIFO** (first-in, first-out): cada compra a un proveedor crea un "lote" con su propio costo unitario, y cada venta consume primero los lotes mas antiguos para calcular la ganancia real, en lugar de usar un costo promedio.

## Problema tecnico que encontre y corregi

El sistema original calculaba y **descontaba** el costo del inventario (de los lotes FIFO) en el momento en que el usuario agregaba un perfume a la lista temporal de una venta, antes de confirmar nada. Si el usuario abria la ventana de "Nueva venta", agregaba perfumes y cerraba la ventana sin guardar, el lote ya habia sido descontado en la base de datos aunque la venta nunca se registro. Esto desincronizaba el costo real de inventario sin que existiera ningun registro de venta que lo explicara.

La correccion separo el problema en dos pasos:

1. `calcular_costo_estimado()` — calcula el costo FIFO **sin modificar la base de datos**, usado solo para mostrar una previsualizacion mientras se arma la venta.
2. `aplicar_descuento_lotes()` — descuenta de verdad las unidades de los lotes, y se ejecuta **unicamente** al confirmar la venta con "Guardar venta".

Tambien se agrego `revertir_descuento_lotes()`, que devuelve las unidades a los lotes (en el mismo orden en que se consumieron) cuando se elimina una venta, para que el costeo FIFO se mantenga consistente incluso despues de una reversion.

Otros problemas corregidos:

- Validacion de existencias que no contaba lo que ya se habia agregado a la lista temporal de la misma venta (permitia vender mas stock del disponible si se agregaba el mismo perfume dos veces).
- Falta de manejo de errores al convertir texto de formularios a numeros: un campo vacio o con texto causaba que la ventana se cerrara de golpe en vez de mostrar un mensaje de error claro.

## Seguridad: usuarios y roles

La primera vez que se abre la app, pide crear una cuenta de administrador. Las siguientes veces, pide usuario y contraseña. Las contraseñas se guardan con hash + salt (nunca en texto plano).

Hay dos roles:

- **admin**: acceso total, incluye crear/eliminar usuarios desde la pantalla "Usuarios".
- **vendedora**: puede registrar ventas, clientes y compras, pero no puede eliminar registros ni editar precios de inventario o proveedores.

## Recibos en PDF

Desde la pantalla de Ventas, seleccionando una venta y presionando "Generar recibo PDF" se crea un PDF en la carpeta `recibos/` con el detalle de la venta (perfume, marca, cantidad, tipo de precio, total) y se abre automaticamente.

## Tests y CI

Los tests automatizados (`tests/`) cubren la logica de costeo FIFO y la autenticacion de usuarios, usando una base de datos SQLite en memoria que no toca los datos reales. Corren automaticamente en cada `push` mediante GitHub Actions (`.github/workflows/tests.yml`).

Para correrlos localmente:

```
pip install pytest
python -m pytest tests/ -v
```

## Stack

Python 3, Tkinter/ttk para la interfaz, SQLite como base de datos local, `gspread` + Google Service Account para la sincronizacion con Google Sheets, `fpdf2` para los recibos en PDF.

## Como correrla

```
pip install -r requirements.txt
python main.py
```

Requiere `Image.png` en la misma carpeta (la imagen de la pantalla de inicio; si no esta, la app abre igual sin mostrarla). `credenciales.json` es opcional, solo se necesita para la sincronizacion con Google Sheets (ver siguiente seccion).

## Sincronizacion con Google Sheets (opcional)

La app puede sincronizar automaticamente los datos de Inventario, Ventas, Clientes, Proveedores y Economia a una hoja de calculo de Google. Esto es opcional: si no la configuras, la app funciona igual usando solo la base de datos local.

Para activarla:

1. Entra a [Google Cloud Console](https://console.cloud.google.com/) y crea un proyecto (o usa uno existente).
2. Habilita las APIs de **Google Sheets** y **Google Drive** para ese proyecto.
3. Crea una **cuenta de servicio** (Service Account) y descarga su archivo de credenciales en formato JSON.
4. Renombra ese archivo a `credenciales.json` y colocalo en la misma carpeta que `main.py`.
5. Crea una hoja de calculo de Google llamada `PERFUMES` (o el nombre que prefieras) con 5 pestañas llamadas exactamente: `Inventario`, `Ventas`, `Clientes`, `Proveedores`, `Economia`.
6. Comparte esa hoja de calculo con el correo de la cuenta de servicio (aparece dentro del `credenciales.json`, campo `client_email`), dandole permiso de Editor.
7. Si usaste un nombre distinto a `PERFUMES`, configuralo con la variable de entorno `PERFUMERIA_SHEET_NAME`.

Si el archivo `credenciales.json` no existe o las credenciales no son validas, la app te avisara al iniciar y seguira funcionando sin sincronizar.