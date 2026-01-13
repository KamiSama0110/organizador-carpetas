# Organizador de Carpetas

Una aplicación gráfica multiplataforma (Linux y Windows) para organizar archivos automáticamente según sus extensiones.

## Características

- ✅ Interfaz gráfica intuitiva con PySide6
- ✅ Soporte multiplataforma (Linux y Windows)
- ✅ Organización basada en reglas de extensión
- ✅ Operaciones de copiar o mover archivos
- ✅ Manejo de conflictos de nombres automático
- ✅ Creación automática de carpetas por extensión

## Requisitos

- Python 3.8+
- PySide6

## Instalación

1. Clona o descarga el proyecto:
```bash
cd Organizador
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecuta la aplicación:
```bash
python main.py
```

### Flujo de uso:

1. **Selecciona la carpeta de origen**: Haz clic en "Seleccionar" para elegir la carpeta que deseas organizar
2. **Añade reglas**: Ingresa las extensiones de archivo que deseas organizar (ej: pdf, exe, txt)
3. **Selecciona la carpeta de destino**: Elige dónde deseas que se organicen los archivos
4. **Elige la operación**: Decide si deseas copiar o mover los archivos
5. **Ejecuta**: Haz clic en "Ejecutar Organización" para iniciar el proceso

## Estructura

- `main.py`: Punto de entrada de la aplicación
- `ui.py`: Interfaz gráfica (PySide6)
- `organizer.py`: Lógica de organización de archivos
- `requirements.txt`: Dependencias del proyecto

## Detalles técnicos

- Usa `pathlib` para manejar rutas de forma multiplataforma
- Crea automáticamente carpetas por extensión en el destino
- Maneja conflictos de nombres automáticamente
- Valida todas las entrada del usuario
- Proporciona retroalimentación detallada de la operación

## Notas

- Los archivos se organizan en subcarpetas según su extensión (sin el punto)
- Si un archivo con el mismo nombre existe en el destino, se renombra automáticamente
- Los errores se capturan y se muestran en el resumen final
