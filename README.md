# 📁 Organizador de Carpetas

Aplicación de escritorio para organizar archivos automáticamente. Clasifica tus archivos por extensión, tipo, tamaño o fecha con una interfaz moderna y fácil de usar.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey.svg)

## ✨ Características

### Organización Inteligente
- **Por extensión**: Crea carpetas automáticas para cada tipo de archivo (.pdf, .jpg, .mp3, etc.)
- **Por categoría**: Agrupa archivos en categorías predefinidas (Imágenes, Documentos, Videos, Audio, etc.)
- **Por tamaño**: Clasifica archivos según su tamaño (Pequeños, Medianos, Grandes, Muy grandes)
- **Por fecha**: Organiza por año, mes o día de modificación

### Operaciones
- **Copiar o Mover**: Elige mantener los originales o moverlos
- **Incluir subcarpetas**: Procesa archivos en carpetas anidadas
- **Límite de profundidad**: Controla hasta qué nivel de subcarpetas procesar
- **Vista previa**: Visualiza los cambios antes de ejecutarlos

### Herramientas Adicionales
- **Detector de duplicados**: Encuentra archivos duplicados por hash MD5
- **Historial de operaciones**: Registro de todas las organizaciones realizadas
- **Deshacer cambios**: Revierte operaciones anteriores
- **Tema oscuro**: Interfaz moderna con colores suaves para la vista

### Categorías Predefinidas

| Categoría | Extensiones |
|-----------|-------------|
| Imágenes | .jpg, .png, .gif, .webp, .svg, .ico, .raw, .heic... |
| Documentos | .pdf, .doc, .docx, .txt, .xls, .xlsx, .ppt, .csv... |
| Videos | .mp4, .avi, .mkv, .mov, .webm, .mpeg... |
| Audio | .mp3, .wav, .flac, .aac, .ogg, .m4a... |
| Comprimidos | .zip, .rar, .7z, .tar, .gz... |
| Ejecutables | .exe, .msi, .deb, .rpm, .AppImage, .sh... |
| Código | .py, .js, .html, .css, .java, .cpp, .ts... |
| Fuentes | .ttf, .otf, .woff, .woff2... |
| Diseño | .psd, .ai, .xd, .fig, .blend... |
| Libros | .epub, .mobi, .azw, .djvu... |

## 🚀 Instalación

### Opción 1: Ejecutable (Sin necesidad de Python)

Descarga el ejecutable desde [Releases](https://github.com/KamiSama0110/organizador-carpetas/releases) y ejecútalo directamente.

| Sistema Operativo | Archivo | Notas |
|-------------------|---------|-------|
| 🐧 Linux | `Organizador` | Dar permisos de ejecución: `chmod +x Organizador` |
| 🪟 Windows | `Organizador.exe` | ⚠️ *No disponible aún* |

> **Nota**: Actualmente solo hay ejecutable para Linux. Los usuarios de Windows deben usar la Opción 2 (desde código fuente) o compilar su propio ejecutable.

### Opción 2: Desde código fuente (Todos los sistemas)

```bash
# Clonar el repositorio
git clone https://github.com/KamiSama0110/organizador-carpetas.git
cd organizador-carpetas

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

## 📖 Uso

### 1. Organizar Archivos

1. **Selecciona carpeta origen** - La carpeta que contiene los archivos a organizar
2. **Configura las opciones**:
   - Tipo de organización (extensión, categoría, tamaño, fecha)
   - Operación (copiar o mover)
   - Incluir subcarpetas (opcional)
3. **Selecciona carpeta destino** - Donde se crearán las carpetas organizadas
4. **Vista previa** - Revisa los cambios antes de aplicarlos
5. **Ejecutar** - Aplica la organización

### 2. Buscar Duplicados

1. Ve a la sección **Duplicados**
2. Selecciona la carpeta a analizar
3. Haz clic en **Buscar Duplicados**
4. Revisa los resultados agrupados por hash
5. Elimina los duplicados que no necesites

### 3. Historial

- Consulta todas las operaciones realizadas
- Cada operación muestra: fecha, archivos procesados, origen y destino
- Opción de **deshacer** para revertir cambios

## 🛠️ Crear Ejecutable

Para crear tu propio ejecutable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="Organizador" main.py
```

El ejecutable se generará en la carpeta `dist/`.

> ⚠️ **Importante**: PyInstaller genera ejecutables **específicos para el sistema operativo** donde se compila:
> - Compilado en Linux → Ejecutable solo para Linux
> - Compilado en Windows → Ejecutable .exe solo para Windows
> - Compilado en Mac → Ejecutable solo para Mac
>
> Si necesitas un ejecutable para otro sistema, debes compilarlo en ese sistema.

## 📁 Estructura del Proyecto

```
organizador-carpetas/
├── main.py          # Punto de entrada
├── ui.py            # Interfaz gráfica (PySide6)
├── organizer.py     # Lógica de organización
├── requirements.txt # Dependencias
└── README.md
```

## 🔧 Requisitos

- Python 3.8 o superior
- PySide6 6.0+

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para cambios importantes:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcion`)
3. Commit de tus cambios (`git commit -m 'Agrega nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

---

Hecho con ❤️ por [KamiSama0110](https://github.com/KamiSama0110)
