# Seguridad

## Reportar una vulnerabilidad

Si encuentras un problema de seguridad en este proyecto, abre un Issue describiendo el problema con el mayor detalle posible (qué archivo, qué función, cómo reproducirlo). Si el problema es sensible y prefieres no hacerlo público de inmediato, contacta directamente al autor del repositorio antes de abrir el Issue.

## Cómo se maneja la información sensible en este proyecto

* Las contraseñas de usuarios de la app se guardan con **hash + salt** (`auth.py`), nunca en texto plano.
* El archivo `credenciales.json` (credenciales de Google Service Account) **nunca debe subirse al repositorio**. Ya está excluido en `.gitignore`; si clonas este proyecto, asegúrate de no quitar esa línea.
* La base de datos (`*.db`), los respaldos (`backups/`), los recibos (`recibos/`), los reportes (`reportes/`) y los logs (`logs/`) tampoco se suben al repositorio, porque contienen datos reales de negocio, no código.
* El archivo `preferencias.json` es configuración local de cada instalación y tampoco se versiona.

## Si vas a usar este proyecto con datos reales

Antes de poner esta app a trabajar con información real de un negocio:

* Cambia el umbral de stock bajo y demás configuraciones según tu caso (`config.py`).
* Crea tu propia cuenta de administrador desde el primer inicio — no reutilices contraseñas de otros sistemas.
* Si vas a habilitar la sincronización con Google Sheets, comparte la hoja de cálculo únicamente con el correo de tu propia cuenta de servicio, con permisos de Editor (no de propietario).
