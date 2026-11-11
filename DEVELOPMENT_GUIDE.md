# Guía de desarrollo — Bionic AI Desktop

Estado y plan del proyecto según el código actual. La aplicación usa PySide6 (no PyQt5), Ollama y SQLite.

## Estado actual

La base funcional incluye:

- Ventana de escritorio con selector de modelos, chat y panel de auditoría.
- Cliente HTTP para consultar Ollama y generar respuestas.
- Persistencia SQLite de conversaciones, mensajes y registros de acciones.
- Registro de herramientas para archivos, comandos y consulta del sistema.
- Diálogo de aprobación y niveles de riesgo.
- Restricción de operaciones de archivos a directorios permitidos.
- Pruebas iniciales de permisos y parsing del agente.

Esto es un MVP. Que arranque y pase pruebas manuales no significa que las herramientas de comandos sean una frontera de seguridad fuerte; antes de distribuirlo hay que endurecerlas y probarlas.

## Preparación del entorno

Requisitos: Python 3.10+ y Ollama instalado. En una terminal, desde la raíz:

```bash
python -m venv .venv
```

Activa el entorno virtual y luego instala dependencias y pruebas:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m compileall app
python run.py
```

En Windows PowerShell, la activación del entorno virtual es:

```powershell
.venv\Scripts\Activate.ps1
```

En macOS/Linux:

```bash
source .venv/bin/activate
```

Ollama debe estar ejecutándose y tener al menos un modelo descargado, por ejemplo `ollama pull llama3.1`.

## Estructura

- `app/main.py`, `run.py`: arranque de la aplicación.
- `app/ui/`: ventana, chat, aprobación y auditoría.
- `app/agent/`: ciclo del agente, permisos y registro/carga de herramientas.
- `app/tools/`: operaciones de archivos, shell y sistema.
- `app/storage/`: persistencia SQLite.
- `app/ollama_client.py`: comunicación con Ollama.
- `app/config.py`: configuración, rutas permitidas y logs.
- `tests/`: pruebas automatizadas.

## Roadmap priorizado

### P0 — Seguridad antes de ampliar capacidades

- Sustituir la lista negra de comandos por una política segura por defecto; no permitir ejecución arbitraria de shell como si fuera segura.
- Validar argumentos y esquema exacto de cada herramienta justo antes de ejecutarla.
- Revalidar rutas tras resolver enlaces simbólicos y bloquear accesos fuera de las carpetas autorizadas.
- Asegurar que aprobaciones de sesión no cubran acciones destructivas o comandos arbitrarios.
- Probar que una denegación nunca ejecuta la acción y que los registros distinguen aprobada, denegada y fallida.

**Listo cuando:** pruebas negativas demuestran que acciones no autorizadas no llegan a la función ejecutora.

### P1 — Pruebas automatizadas y CI

- Añadir pruebas aisladas de cada herramienta usando directorios temporales y mocks.
- Cubrir aprobaciones aceptadas/denegadas, errores, rutas, argumentos inválidos y respuestas malformadas del modelo.
- Probar regresiones de UI y el bloqueo de mensajes concurrentes.
- Añadir GitHub Actions para ejecutar `python -m pytest -q` en cada pull request.

**Listo cuando:** la suite es determinista, no modifica archivos del usuario y corre sin Ollama real.

### P2 — Conversación y fiabilidad

- Pasar el historial de la conversación al modelo; actualmente el flujo de generación debe verificarse para asegurar continuidad entre turnos.
- Gestionar estados de generación/aprobación, evitar workers concurrentes y permitir recuperación limpia ante errores.
- Mejorar mensajes para Ollama caído, modelo inexistente, timeout y error de herramienta.
- Guardar de forma consistente en auditoría las acciones aprobadas, denegadas y fallidas.

### P3 — Experiencia de usuario

- Mostrar estado de trabajo y herramienta solicitada antes de la aprobación.
- Añadir cancelación segura de generación y controles de conversación.
- Permitir exportar conversaciones y seleccionar/recordar modelo preferido.
- Añadir accesibilidad, traducciones y temas una vez estable el flujo principal.

### P4 — Distribución

- Definir plataforma objetivo (primero Windows si ese es el caso principal).
- Crear empaquetado reproducible, instalador y manejo de datos/logs fuera de la carpeta de instalación.
- Documentar actualización, desinstalación, privacidad y permisos.
- Preparar versión, changelog y publicación después de completar P0–P2.

## Pruebas manuales de aceptación

1. Iniciar con Ollama apagado: la app debe explicar que no conecta, sin colgarse.
2. Iniciar con Ollama y un modelo disponible: el modelo aparece y un mensaje normal recibe respuesta.
3. Solicitar una operación de archivo permitida: revisar parámetros en el diálogo, denegar y confirmar que no se hizo; repetir aprobando y comprobar resultado y auditoría.
4. Intentar una ruta fuera de la lista permitida: debe rechazarse.
5. Probar una llamada de herramienta mal formada y un nombre de herramienta desconocido: no debe ejecutarse ninguna función.
6. Intentar enviar otro mensaje durante una generación: no debe crear otra ejecución en paralelo.
7. Revisar la pestaña de auditoría después de éxito, denegación y fallo.

No probar comandos destructivos reales en la máquina. Para validar bloqueos, usar pruebas unitarias/mocks, no ejecutarlos en la terminal.

## Nota de consistencia documental

El README debe decir PySide6, que es lo que importa `app/main.py` y declara `requirements.txt`; eliminar la referencia antigua a PyQt5 para evitar instrucciones contradictorias.
