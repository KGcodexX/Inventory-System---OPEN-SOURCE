# Sistema de Gestión para Perfumería

Esta es una aplicación de escritorio diseñada a la medida para centralizar y simplificar el día a día de un negocio de venta de perfumes. Lejos de ser un proyecto puramente teórico, la aplicación opera actualmente en un entorno real, unificando el control de inventario, ventas, clientes, proveedores y finanzas en una sola plataforma rápida e intuitiva.

## ¿Por qué nació este proyecto?

Antes de implementar este sistema, el negocio gestionaba toda su información de forma manual. Esto generaba los problemas típicos de cualquier comercio: errores constantes al calcular las ganancias netas (debido a que un mismo producto se compraba en distintas fechas a costos diferentes) y horas perdidas revisando anotaciones para conocer el stock disponible, identificar a los clientes frecuentes o cuadrar la caja del día.

El objetivo principal fue automatizar estas tareas operativas y devolverle el control estratégico al dueño del negocio a través de una herramienta ágil, limpia y fácil de adoptar.

---

## Funcionalidades Clave

### Control de acceso y seguridad de usuarios

El sistema garantiza la seguridad de la información mediante credenciales de acceso y maneja dos perfiles bien definidos:

* **Administrador**: Cuenta con privilegios totales para gestionar configuraciones, modificar precios y evaluar la economía del negocio.
* **Vendedora**: Tiene un acceso enfocado exclusivamente en la operación diaria (ventas y consultas), restringiendo acciones críticas como la alteración de precios o el borrado de registros.

**Detalle técnico:** Las contraseñas se protegen bajo estándares modernos utilizando encriptación avanzada (hash + salt) en lugar de texto plano.

---

### Panel de inicio e información inmediata

Nada más abrir la aplicación, el usuario recibe un diagnóstico visual e inmediato del estado del negocio: total vendido, ganancias del día y un recuento de los artículos que están por agotarse. El aviso de inventario bajo cuenta con un switch en la misma pantalla para activarse o desactivarse según las necesidades del flujo de trabajo.

---

### Gestión inteligente de inventario

Permite registrar, actualizar y dar de baja productos de forma individual, con un buscador por nombre que localiza cualquier perfume en segundos, eliminando las consultas lentas en papel o en hojas de cálculo.

---

### Ventas precisas con costeo financiero

Cada transacción registra de manera transparente el método de pago, el tipo de precio aplicado (normal, mayoreo o personalizado) y la cantidad vendida. El historial completo se puede filtrar por cliente o por rangos de fechas para realizar auditorías rápidas sin navegar por todo el histórico. Este módulo permite evaluar con exactitud el margen de utilidad real de cada operación.

---

### Seguimiento de clientes y fidelización

El sistema permite crear perfiles de clientes y consultar su historial completo de compras. Es una herramienta ideal para identificar patrones de consumo y recompensar a los compradores más fieles.

---

### Control de proveedores y trazabilidad

Cada compra registrada a un proveedor genera automáticamente nuevos lotes de inventario asociados a su costo específico de adquisición. Esta información es la que utiliza el sistema más adelante para mantener las finanzas impecables.

---

### Módulo de economía y analítica integral

Diseñado para la toma de decisiones basada en datos, este panel ofrece indicadores avanzados como:

* Rendimiento de ventas y utilidades diarias y mensuales.
* Ranking de perfumes más vendidos y detección de productos con menor rotación.
* Clientes de mayor volumen comercial.
* **Predicción de existencias:** El sistema evalúa la velocidad de salida de cada perfume durante los últimos 30 días para proyectar cuántos días de inventario quedan antes de agotar stock.

Incluye gráficas visuales y un botón dedicado para exportar todo este balance financiero a un reporte profesional en PDF.

---

### Emisión de recibos digitales

Desde la pantalla de ventas se pueden generar comprobantes en formato PDF de manera inmediata, desglosando la marca, cantidad, tipo de precio aplicado y el total de la transacción para el cliente.

---

### Sincronización en la nube con Google Sheets (Opcional)

Para mayor flexibilidad, el sistema puede enviar los datos automáticamente a una hoja de cálculo de Google. Esta tarea se procesa en segundo plano para que la interfaz nunca se congele o se vuelva lenta. Si no hay conexión o no se configura la API, el software trabaja de manera local sin afectar el rendimiento.

---

### Respaldos automáticos y auditoría técnica

La integridad de los datos es crucial. El sistema genera una copia de seguridad en la carpeta `backups/` cada vez que se inicia la aplicación o antes de ejecutar operaciones de borrado. Si ocurre un imprevisto técnico, el error se almacena discretamente en `logs/app.log` para facilitar un diagnóstico rápido sin interrumpir la experiencia del usuario.

---

## Arquitectura del Proyecto

El código está estructurado bajo un enfoque modular, donde cada componente tiene una responsabilidad única y aislada, facilitando el mantenimiento y escalabilidad del software:

| Archivo / Carpeta | Propósito y Responsabilidad |
|---|---|
| `main.py` | Punto de entrada principal y gestor de excepciones globales. |
| `app.py` | Control de la ventana principal, enrutamiento y el panel de inicio. |
| `config.py` | Definición de constantes del sistema, paleta de colores y fuentes. |
| `db.py` | Gestión de la base de datos SQLite, esquemas y copias de seguridad. |
| `auth.py` / `login.py` | Manejo de sesiones, seguridad y creación del administrador inicial. |
| `usuarios.py` | Control, registro y permisos del personal. |
| `preferencias.py` | Persistencia de configuraciones locales de usuario. |
| `recibos.py` / `reportes.py` | Motores de diseño y exportación de documentos PDF (fpdf2). |
| `registro.py` | Configuración y formateo del sistema de logs. |
| `sheets.py` | Lógica de integración y comunicación con la API de Google. |
| `styles.py` / `widgets.py` | Estilos de la interfaz con ttk y diseño de componentes visuales reutilizables. |
| `inventario.py`, `ventas.py`, etc. | Interfaces y lógica de negocio para cada pantalla del sistema. |
| `tests/` | Suites de pruebas automatizadas. |

---

## Retos Técnicos y Soluciones

### El desafío del costo real con el método FIFO

Calcular las ganancias basándose en costos promedio suele distorsionar la salud financiera de un negocio si los precios de los proveedores fluctúan. Para resolver esto, implementé el algoritmo FIFO (First In, First Out). El sistema realiza un seguimiento estricto de cada lote por separado; al procesar una venta, se descuentan primero las unidades del lote más antiguo en existencia, lo que permite calcular el margen de ganancia con mucha más precisión que usando un costo promedio.

### El problema del "Inventario Fantasma" y la consistencia de datos

Durante el desarrollo se detectó un problema crítico: los productos se restaban del inventario tan pronto como se añadían al carrito temporal de una venta. Si el usuario cancelaba la transacción a mitad del proceso, el stock ya había cambiado, generando discrepancias severas entre los productos físicos y la base de datos.

La solución consistió en rediseñar el flujo en dos etapas atómicas:

* `calcular_costo_estimado()`: Consulta el inventario mediante la lógica FIFO y genera una vista previa del costo total y la ganancia simulada, sin tocar la base de datos.
* `aplicar_descuento_lotes()`: Modifica definitivamente el inventario y consolida los lotes únicamente cuando la venta es confirmada y registrada de forma segura.

Además, se diseñó la rutina `revertir_descuento_lotes()`, encargada de reincorporar las unidades de manera exacta a sus lotes originales en caso de que una venta confirmada sea eliminada del historial. También se añadieron validaciones para evitar que campos vacíos o con datos inválidos (texto en lugar de números, por ejemplo) provocaran cierres inesperados de la interfaz.

---

## Pruebas Automatizadas

Para garantizar la fiabilidad del núcleo del sistema, el proyecto cuenta con pruebas unitarias que validan:

* El comportamiento exacto del algoritmo de costeo FIFO ante diferentes escenarios de compra y venta.
* El flujo de autenticación y restricciones de seguridad por rol de usuario.

Estas pruebas utilizan una base de datos SQLite en memoria (`:memory:`), aislando por completo los entornos de prueba de los datos reales del negocio. Además, están integradas en un flujo de Integración Continua (CI) mediante GitHub Actions, ejecutándose de forma automática con cada actualización del repositorio.

Para lanzar las pruebas en un entorno local:

```bash
pip install pytest
python -m pytest tests/ -v
Tecnologías Utilizadas
Lenguaje: Python 3
Interfaz Gráfica: Tkinter / ttk
Base de Datos: SQLite
Integración Cloud: gspread y Google Service Account
Reportería e Ingeniería Visual: fpdf2, matplotlib y Pillow
Despliegue y Ejecución
Para iniciar el proyecto en un entorno local, asegúrate de instalar las dependencias necesarias e inicializar el archivo principal:

pip install -r requirements.txt
python main.py
Nota sobre la interfaz: El sistema busca un archivo llamado Image.png como pantalla de bienvenida. Si no se encuentra presente, la aplicación está diseñada para mitigar el error y continuar funcionando normalmente.

Nota sobre la nube: El archivo credenciales.json es un requisito exclusivo si deseas activar la sincronización con Google Sheets. Si no se incluye, el sistema ignorará el paso y trabajará de forma local de manera transparente.

Configuración de Google Sheets (Opcional)
Si deseas habilitar el respaldo automático en la nube, sigue estos pasos:

Crea un proyecto dentro de Google Cloud Console.
Habilita las APIs de Google Sheets y Google Drive para dicho proyecto.
Genera una Cuenta de Servicio (Service Account) y descarga su archivo de credenciales en formato JSON.
Renombra el archivo descargado como credenciales.json y colócalo en el directorio raíz, al mismo nivel que main.py.
Abre tu hoja de cálculo de Google y compártela con la dirección de correo generada en la Cuenta de Servicio, otorgándole permisos de edición.
Si las credenciales faltan o contienen errores, el sistema está diseñado para no interrumpir la operación del negocio, continuando su ejecución en modo local.

Licencia
Este proyecto se distribuye bajo la licencia MIT. Eres completamente libre de usarlo, modificar el código y distribuirlo tanto para fines académicos como comerciales.