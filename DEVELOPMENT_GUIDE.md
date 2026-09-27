# Guía de Desarrollo: Bionic AI Desktop

Guía paso a paso para crear una aplicación de escritorio con IA local que pueda controlar tu PC.

## Fases de Desarrollo

### Fase 1: Base del Proyecto ✅ (Completado)

1. ✅ Crear repositorio en GitHub
2. ✅ Estructura de carpetas
3. ✅ Configuración inicial (config.py)
4. ✅ Cliente de Ollama (ollama_client.py)
5. ✅ Base de datos (database.py)
6. ✅ UI principal con PySide6
7. ✅ Chat básico funcional
8. ✅ Selector de modelos
9. ✅ Historial de conversaciones
10. ✅ Panel de auditoría

### Fase 2: Sistema de Herramientas (EN PROGRESO)

11. ⏳ Crear ToolRegistry (registro de herramientas)
12. ⏳ Registrar herramientas disponibles
13. ⏳ Crear sistema de permisos mejorado
14. ⏳ Implementar diálogo de aprobación
15. ⏳ Herramienta: crear carpetas
16. ⏳ Herramienta: leer archivos
17. ⏳ Herramienta: escribir archivos
18. ⏳ Herramienta: listar carpetas
19. ⏳ Herramienta: ejecutar comandos CMD
20. ⏳ Herramienta: ejecutar PowerShell

### Fase 3: Agente Autónomo (Próximo)

21. ⏳ Crear AgentLoop (lógica del agente)
22. ⏳ Hacer que la IA entienda qué herramientas puede usar
23. ⏳ Solicitar permisos automáticamente
24. ⏳ Ejecutar herramientas con confirmación del usuario
25. ⏳ Procesar respuesta y continuar conversación
26. ⏳ Manejo de errores en herramientas
27. ⏳ Logging detallado de acciones

### Fase 4: Más Herramientas (Expandir)

28. ⏳ Herramientas de información del sistema
29. ⏳ Herramientas de procesos
30. ⏳ Herramientas de internet
31. ⏳ Herramientas de búsqueda de archivos
32. ⏳ Herramientas de edición de código

### Fase 5: Mejoras de UI (Refinar)

33. ⏳ Mostrar estado de herramientas en UI
34. ⏳ Animaciones de carga
35. ⏳ Indicador de permisos pendientes
36. ⏳ Modo oscuro
37. ⏳ Tema personalizable

### Fase 6: Streaming Real (Optimizar)

38. ⏳ Implementar streaming de respuestas
39. ⏳ Mostrar respuesta mientras se genera
40. ⏳ Mejorar rendimiento

### Fase 7: Empaquetar (Deploy)

41. ⏳ Crear ejecutable para Windows
42. ⏳ Crear instalador
43. ⏳ Documentación completa
44. ⏳ Publicar

---

## Detalles por Fase

### Fase 2: Sistema de Herramientas (DESGLOSE)

#### 11. Crear ToolRegistry

**Archivo:** `app/agent/tool_registry.py` ✅ (ya existe)

**Qué hace:**
- Registro central de todas las herramientas disponibles
- Permite registrar, listar y ejecutar herramientas
- Cada herramienta tiene nombre, descripción, función y nivel de permiso

**Código base ya existe, necesita:**
- Mejorar manejo de excepciones
- Validación de parámetros
- Logging detallado

#### 12. Registrar herramientas disponibles

**Archivo:** `app/agent/tools_loader.py` (CREAR)

**Qué hace:**
- Carga todas las herramientas al iniciar la app
- Las registra en el ToolRegistry
- Define permisos para cada una

**Ejemplo:**
```python
registry = ToolRegistry()

# Herramientas de archivos (MEDIUM risk)
registry.register(
    name="create_folder",
    description="Crear una carpeta",
    func=file_tools.create_folder,
    permission_level=PermissionLevel.MEDIUM,
    parameters={"folder_path": "str"}
)

registry.register(
    name="read_file",
    description="Leer contenido de un archivo",
    func=file_tools.read_file,
    permission_level=PermissionLevel.LOW,
    parameters={"file_path": "str"}
)
```

#### 13. Crear sistema de permisos mejorado

**Archivo:** `app/agent/permission_manager.py` ✅ (ya existe, mejorar)

**Qué hace:**
- Define 3 niveles de riesgo: LOW, MEDIUM, HIGH
- Valida acciones antes de ejecutar
- Mantiene whitelist de carpetas permitidas
- Mantiene blacklist de comandos peligrosos

**Mejoras necesarias:**
- Agregar permisos por herramienta específica
- Sistema de "permisos por sesión"
- Historial de permisos otorgados

#### 14. Implementar diálogo de aprobación

**Archivo:** `app/ui/approval_dialog.py` (CREAR)

**Qué hace:**
- Ventana modal que muestra la acción que la IA quiere hacer
- Muestra: herramienta, parámetros, riesgo, descripción
- Botones: Permitir, Denegar, Permitir en esta sesión
- Vista previa del comando/acción

**Ejemplo visual:**
```
┌─────────────────────────────────────────┐
│  Solicitud de Permiso                   │
├─────────────────────────────────────────┤
│ Riesgo: ⚠️  MEDIO                       │
│                                         │
│ Herramienta: create_folder              │
│ Acción: Crear carpeta                   │
│                                         │
│ Parámetros:                             │
│  • folder_path: "C:\Users\...\Proyecto" │
│                                         │
│ ¿Permitir esta acción?                  │
│                                         │
│  [Permitir]  [Denegar]  [Sesión]       │
└─────────────────────────────────────────┘
```

#### 15-20. Herramientas individuales

**Archivos ya existen:**
- `app/tools/file_tools.py` ✅
- `app/tools/shell_tools.py` ✅
- `app/tools/system_tools.py` ✅

**Qué hace cada una:**

**file_tools.py:**
- `read_file(path)` - Lee archivo
- `write_file(path, content)` - Escribe archivo
- `create_folder(path)` - Crea carpeta
- `delete_file(path)` - Elimina archivo
- `list_files(path)` - Lista carpeta
- `copy_file(src, dst)` - Copia archivo

**shell_tools.py:**
- `execute_command(cmd)` - Ejecuta CMD
- `execute_powershell(cmd)` - Ejecuta PowerShell

**system_tools.py:**
- `get_system_info()` - Info del sistema
- `list_processes()` - Procesos
- `kill_process(pid)` - Detiene proceso

---

### Fase 3: Agente Autónomo (PRÓXIMO)

#### 21. Crear AgentLoop

**Archivo:** `app/agent/agent_loop.py` (CREAR)

**Qué hace:**
- Loop principal del agente
- Recibe prompt del usuario
- Genera respuesta con Ollama
- Detecta si quiere usar herramientas
- Solicita permisos
- Ejecuta herramientas
- Retorna resultado

**Pseudocódigo:**
```python
class AgentLoop:
    def run(self, user_prompt: str):
        # 1. Enviar a Ollama con descripción de herramientas
        response = ollama.generate(
            prompt=user_prompt,
            tools_description=self.get_tools_description()
        )
        
        # 2. Parsear si la IA quiere usar una herramienta
        if "[TOOL]" in response:
            tool_name, params = parse_tool_request(response)
            
            # 3. Solicitar permiso
            approved = ask_user_permission(tool_name, params)
            
            if approved:
                # 4. Ejecutar
                result = execute_tool(tool_name, params)
                
                # 5. Procesar resultado
                final_response = ollama.generate(
                    prompt=f"Resultado: {result}. Explica qué hiciste."
                )
                return final_response
        
        return response
```

#### 22-27. Implementación del agente

**Pasos:**
- Hacer que la IA sepa qué herramientas existen
- Enseñarle el formato para solicitar herramientas
- Capturar solicitudes de herramientas
- Mostrar diálogo de confirmación
- Ejecutar herramienta
- Procesar resultado
- Continuar conversación

---

### Fase 4: Más Herramientas (EXPANDIR)

#### 28-32. Nuevas categorías

**28. Información del sistema:**
- CPU, RAM, Disco
- Procesos activos
- Versión de Windows
- IP de red

**29. Procesos:**
- Listar procesos
- Iniciar proceso
- Detener proceso
- Información de proceso

**30. Internet:**
- Abrir navegador
- Buscar en Google
- Descargar archivo
- Abrir URL

**31. Búsqueda:**
- Buscar archivos por nombre
- Buscar archivos por tipo
- Buscar contenido dentro de archivos

**32. Código:**
- Crear proyecto
- Leer código
- Editar código
- Ejecutar script Python

---

### Fase 5: Mejoras de UI (REFINAR)

**Cambios en la interfaz:**
- Panel de herramientas disponibles
- Indicador de "permiso pendiente"
- Animación de carga
- Estado de ejecución
- Modo oscuro/claro
- Historial detallado con herramientas usadas

---

### Fase 6: Streaming Real (OPTIMIZAR)

**Mejoras de rendimiento:**
- Mostrar respuesta mientras se genera (no esperar a terminar)
- Streaming en tiempo real
- Mejor UX

---

### Fase 7: Empaquetar (DEPLOY)

**Para Windows:**
- PyInstaller para crear .exe
- Instalador con NSIS
- Icono personalizado
- Acceso directo en menú inicio

---

## Próximos Pasos Recomendados

**Inmediato (Esta semana):**
1. ✅ Crear `app/ui/approval_dialog.py` - Diálogo de aprobación
2. ✅ Crear `app/agent/tools_loader.py` - Loader de herramientas
3. ✅ Crear `app/agent/agent_loop.py` - Loop del agente
4. ✅ Integrar todo en `main_window.py`
5. ✅ Probar que la IA puede crear carpetas con permiso

**Después:**
- Agregar más herramientas
- Mejorar UI
- Streaming real
- Empaquetar

---

## Archivos a Crear/Modificar

| Paso | Archivo | Tipo | Prioridad |
|------|---------|------|-----------|
| 11 | `tool_registry.py` | ✅ Existe | Mejorar |
| 12 | `tools_loader.py` | 🆕 CREAR | 🔴 Alta |
| 13 | `permission_manager.py` | ✅ Existe | Mejorar |
| 14 | `approval_dialog.py` | 🆕 CREAR | 🔴 Alta |
| 21 | `agent_loop.py` | 🆕 CREAR | 🔴 Alta |
| 25 | `main_window.py` | Modificar | 🔴 Alta |

---

## Checklist de Completitud

### Fase 2: Sistema de Herramientas
- [ ] ToolRegistry funcional
- [ ] tools_loader.py creado
- [ ] approval_dialog.py creado y funcional
- [ ] create_folder funciona con aprobación
- [ ] read_file funciona con aprobación
- [ ] write_file funciona con aprobación
- [ ] Auditoría registra herramientas usadas

### Fase 3: Agente Autónomo
- [ ] agent_loop.py creado
- [ ] Detecta solicitudes de herramientas
- [ ] Solicita permisos automáticamente
- [ ] Ejecuta herramientas aprobadas
- [ ] Procesa resultados
- [ ] Continúa conversación

### Fase 4: Más Herramientas
- [ ] Sistema tools
- [ ] Internet tools
- [ ] Búsqueda tools
- [ ] Código tools

---

Esta es la roadmap completa para **Bionic AI Desktop**. ¿Empezamos con la Fase 2?
