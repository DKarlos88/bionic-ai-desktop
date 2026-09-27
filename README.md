# Bionic AI Desktop

Aplicación de escritorio para chatear con modelos de IA locales usando Ollama, con capacidad de controlar tu PC con autorización explícita.

## Características

✨ **Chat con IA Local**: Usa modelos como LLaMA, Mistral, Qwen directamente en tu PC.

🔧 **Acceso a herramientas**: La IA puede leer archivos, ejecutar comandos, gestionar procesos y más.

✅ **Autorización controlada**: Cada acción requiere tu aprobación explícita.

📋 **Auditoría completa**: Registro de todas las acciones realizadas.

📊 **Información del sistema**: Monitoreo de CPU, RAM y procesos.

💾 **Historial persistente**: Guarda todas tus conversaciones.

## Requisitos

- Python 3.10+
- Ollama instalado y ejecutándose
- Al menos un modelo descargado (ej: llama3.1, mistral, qwen2.5)

## Instalación rápida

### 1. Instalar Ollama

Descárgalo desde: https://ollama.com/download

### 2. Descargar un modelo local

```bash
ollama pull llama3.1
```

Otras opciones:
```bash
ollama pull mistral
ollama pull qwen2.5
ollama pull deepseek-r1
```

### 3. Clonar repositorio

```bash
git clone https://github.com/DKarlos88/bionic-ai-desktop.git
cd bionic-ai-desktop
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar la app

```bash
python run.py
```

## Uso

1. **Asegúrate de que Ollama está ejecutándose**
   ```bash
   ollama serve
   ```

2. **Abre la aplicación**
   ```bash
   python run.py
   ```

3. **Selecciona un modelo** de la lista desplegable

4. **Escribe tu mensaje** y presiona Enviar

5. **Para acciones del sistema**, la IA te solicitará autorización

## Herramientas disponibles

### Lectura y análisis
- Leer archivos
- Listar carpetas
- Buscar archivos
- Analizar documentos

### Modificación de archivos
- Crear archivos
- Escribir contenido
- Copiar archivos
- Crear carpetas

### Ejecución de comandos
- Ejecutar comandos CMD
- Ejecutar PowerShell
- Scripts Python

### Sistema
- Ver información del sistema
- Listar procesos
- Gestionar procesos

### Seguridad
- Todos los comandos peligrosos están bloqueados
- Requiere autorización explícita antes de ejecutar
- Acceso restringido a carpetas específicas
- Registro completo de todas las acciones

## Configuración

Edita `app/config.py` para personalizar:

```python
# URL de Ollama
OLLAMA_BASE_URL = "http://localhost:11434"

# Modelo por defecto
DEFAULT_MODEL = "llama3.1"

# Carpetas permitidas
ALLOWED_PATHS = [
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Downloads",
]
```

## Estructura del proyecto

```
bionic-ai-desktop/
├── app/
│   ├── agent/              # Lógica del agente
│   │   ├── permission_manager.py
│   │   ├── tool_registry.py
│   │   └── __init__.py
│   ├── tools/              # Herramientas disponibles
│   │   ├── file_tools.py
│   │   ├── shell_tools.py
│   │   ├── system_tools.py
│   │   └── __init__.py
│   ├── storage/            # Base de datos
│   │   ├── database.py
│   │   └── __init__.py
│   ├── ui/                 # Interfaz de usuario
│   │   ├── main_window.py
│   │   ├── chat_widget.py
│   │   ├── audit_widget.py
│   │   └── __init__.py
│   ├── config.py           # Configuración
│   ├── ollama_client.py    # Cliente de Ollama
│   ├── main.py             # Punto de entrada
│   └── __init__.py
├── data/                   # Base de datos y configuración
├── logs/                   # Archivos de log
├── requirements.txt        # Dependencias Python
├── run.py                  # Ejecutable
└── README.md
```

## Troubleshooting

### "No se puede conectar a Ollama"

Asegúrate de que Ollama está ejecutándose:
```bash
ollama serve
```

### "No hay modelos disponibles"

Descarga un modelo:
```bash
ollama pull llama3.1
```

### La app es lenta

Es normal con modelos grandes. Usa modelos más pequeños:
```bash
ollama pull mistral  # Más rápido
```

## Mejoras futuras

- [ ] Streaming de respuestas en tiempo real
- [ ] Interfaz gráfica avanzada con temas
- [ ] Edición de prompts avanzados
- [ ] Exportar conversaciones
- [ ] Integración con APIs externas
- [ ] Múltiples sesiones simultáneas
- [ ] Automatización visual (PyAutoGUI)
- [ ] Historial de comandos ejecutados
- [ ] Permisos granulares por herramienta

## Seguridad

⚠️ **Importante**: Esta aplicación te da a la IA acceso a tu PC. 

Medidas de seguridad implementadas:
- Autorización explícita antes de cada acción
- Lista negra de comandos peligrosos
- Restricción de acceso a carpetas específicas
- Registro completo de todas las acciones
- Timeout en comandos
- Validación de parámetros

## Licencia

MIT License - Ver LICENSE para detalles

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Soporte

Si tienes problemas o sugerencias, abre un [Issue](https://github.com/DKarlos88/bionic-ai-desktop/issues).

---

**Made with ❤️ by DKarlos88**
