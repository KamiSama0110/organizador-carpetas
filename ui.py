from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QComboBox, QGroupBox, QMessageBox, QCheckBox, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, 
    QDialog, QDialogButtonBox, QSpinBox, QStackedWidget, QFrame,
    QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QColor, QFont, QIcon
from pathlib import Path
from organizer import FileOrganizer, EXTENSION_CATEGORIES


DARK_STYLE = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #3a3a5a;
    border-radius: 8px;
    margin-top: 12px;
    padding: 15px;
    padding-top: 25px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    color: #4fc3f7;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #16213e;
    border: 1px solid #3a3a5a;
    border-radius: 6px;
    padding: 8px 12px;
    color: #eaeaea;
    min-height: 20px;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #4fc3f7;
}
QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}
QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}
QPushButton {
    background-color: #0f3460;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #1a4f7a;
}
QPushButton:pressed {
    background-color: #0a2540;
}
QPushButton:disabled {
    background-color: #2a2a4a;
    color: #6a6a8a;
}
QPushButton#menuBtn {
    background-color: transparent;
    border-radius: 8px;
    padding: 12px 20px;
    text-align: left;
    font-weight: normal;
}
QPushButton#menuBtn:hover {
    background-color: #0f3460;
}
QPushButton#menuBtn:checked {
    background-color: #0f3460;
    border-left: 3px solid #4fc3f7;
}
QPushButton#executeBtn {
    background-color: #1b998b;
    font-size: 14px;
}
QPushButton#executeBtn:hover {
    background-color: #2ab7a7;
}
QPushButton#dangerBtn {
    background-color: #e94560;
}
QPushButton#dangerBtn:hover {
    background-color: #f05575;
}
QListWidget, QTableWidget {
    background-color: #16213e;
    border: 1px solid #3a3a5a;
    border-radius: 6px;
    padding: 5px;
}
QListWidget::item {
    padding: 5px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #0f3460;
}
QTableWidget {
    gridline-color: #3a3a5a;
}
QTableWidget QHeaderView::section {
    background-color: #0f3460;
    color: #eaeaea;
    padding: 8px;
    border: none;
    font-weight: bold;
}
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #16213e;
    text-align: center;
    color: white;
    min-height: 25px;
}
QProgressBar::chunk {
    background-color: #4fc3f7;
    border-radius: 6px;
}
QCheckBox {
    spacing: 10px;
    padding: 5px;
}
QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #3a3a5a;
    background-color: #16213e;
}
QCheckBox::indicator:checked {
    background-color: #4fc3f7;
    border-color: #4fc3f7;
}
QCheckBox::indicator:hover {
    border-color: #4fc3f7;
}
QScrollBar:vertical {
    background-color: #16213e;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #3a3a5a;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #4a4a6a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
#sidebar {
    background-color: #16213e;
    border-right: 1px solid #3a3a5a;
}
#contentArea {
    background-color: #1a1a2e;
}
QLabel#sectionTitle {
    font-size: 18px;
    font-weight: bold;
    color: #4fc3f7;
    padding: 10px 0;
}
QLabel#statusLabel {
    color: #8a8aaa;
    font-size: 12px;
}
"""


class WorkerThread(QThread):
    """Thread para operaciones en segundo plano."""
    progress = Signal(int, int)
    finished = Signal(bool, str)
    
    def __init__(self, organizer, operation="organize"):
        super().__init__()
        self.organizer = organizer
        self.operation = operation
    
    def run(self):
        if self.operation == "organize":
            success, message = self.organizer.organize(self.progress.emit)
        elif self.operation == "scan":
            self.organizer.get_files(self.progress.emit)
            success, message = True, f"Encontrados {len(self.organizer._preview_files)} archivos"
        elif self.operation == "duplicates":
            self.organizer.find_duplicates(self.progress.emit)
            count = self.organizer.duplicate_finder.get_duplicate_count()
            success, message = True, f"Encontrados {count} archivos duplicados"
        elif self.operation == "undo":
            success, message = self.organizer.undo_last(self.progress.emit)
        else:
            success, message = False, "Operación desconocida"
        
        self.finished.emit(success, message)


class PreviewDialog(QDialog):
    """Diálogo para vista previa de archivos."""
    
    def __init__(self, files: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vista Previa de Archivos")
        self.setMinimumSize(700, 450)
        self.files = files
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        info_label = QLabel(f"📋 Se procesarán {len(self.files)} archivos:")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(info_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nombre", "Tipo", "Tamaño", "Modificado"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setRowCount(len(self.files))
        self.table.setAlternatingRowColors(True)
        
        for i, file in enumerate(self.files):
            self.table.setItem(i, 0, QTableWidgetItem(file["name"]))
            self.table.setItem(i, 1, QTableWidgetItem(file["extension"]))
            self.table.setItem(i, 2, QTableWidgetItem(file["size_formatted"]))
            self.table.setItem(i, 3, QTableWidgetItem(file["modified_date"][:10]))
        
        layout.addWidget(self.table)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class DuplicatesDialog(QDialog):
    """Diálogo para mostrar archivos duplicados."""
    
    def __init__(self, duplicates: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Archivos Duplicados")
        self.setMinimumSize(800, 500)
        self.duplicates = duplicates
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        total_dup = sum(len(files) - 1 for files in self.duplicates.values())
        wasted = sum(files[0].size * (len(files) - 1) for files in self.duplicates.values() if files)
        wasted_formatted = self._format_size(wasted)
        
        info_label = QLabel(f"🔍 {total_dup} archivos duplicados | 💾 Espacio desperdiciado: {wasted_formatted}")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(info_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Archivo", "Ubicación", "Tamaño", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        rows = []
        for hash_val, files in self.duplicates.items():
            for i, file in enumerate(files):
                rows.append((file.name, str(file.path.parent), file.get_size_formatted(), 
                           "Original" if i == 0 else "Duplicado"))
        
        self.table.setRowCount(len(rows))
        for i, (name, path, size, status) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(path))
            self.table.setItem(i, 2, QTableWidgetItem(size))
            status_item = QTableWidgetItem(status)
            if status == "Duplicado":
                status_item.setForeground(QColor("#ff9800"))
            self.table.setItem(i, 3, status_item)
        
        layout.addWidget(self.table)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
    
    def _format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"


class HistoryDialog(QDialog):
    """Diálogo para mostrar el historial."""
    
    def __init__(self, history: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Operaciones")
        self.setMinimumSize(600, 400)
        self.history = history
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Fecha/Hora", "Operación", "Archivos"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setRowCount(len(self.history))
        
        for i, batch in enumerate(self.history):
            self.table.setItem(i, 0, QTableWidgetItem(batch["timestamp"][:19].replace("T", " ")))
            op_type = "Movido" if batch["type"] == "move" else "Copiado"
            self.table.setItem(i, 1, QTableWidgetItem(op_type))
            self.table.setItem(i, 2, QTableWidgetItem(str(len(batch.get("operations", [])))))
        
        layout.addWidget(self.table)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class OrganizerWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        self.organizer = FileOrganizer()
        self.setWindowTitle("📁 Organizador de Carpetas")
        self.setMinimumSize(900, 650)
        self.setStyleSheet(DARK_STYLE)
        self.init_ui()
    
    def create_scroll_page(self, page_widget):
        """Envuelve un widget de página en un QScrollArea."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page_widget)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background-color: #16213e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a5a;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a6a;
            }
        """)
        return scroll
    
    def init_ui(self):
        """Inicializa la interfaz gráfica."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)
        
        title = QLabel("📁 Organizador")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4fc3f7; padding: 10px;")
        sidebar_layout.addWidget(title)
        
        sidebar_layout.addSpacing(20)
        
        self.menu_buttons = []
        
        btn_organize = QPushButton("🗂️  Organizar")
        btn_organize.setObjectName("menuBtn")
        btn_organize.setCheckable(True)
        btn_organize.setChecked(True)
        btn_organize.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(btn_organize)
        self.menu_buttons.append(btn_organize)
        
        btn_filters = QPushButton("🔍  Filtros")
        btn_filters.setObjectName("menuBtn")
        btn_filters.setCheckable(True)
        btn_filters.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(btn_filters)
        self.menu_buttons.append(btn_filters)
        
        btn_tools = QPushButton("🛠️  Herramientas")
        btn_tools.setObjectName("menuBtn")
        btn_tools.setCheckable(True)
        btn_tools.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(btn_tools)
        self.menu_buttons.append(btn_tools)
        
        sidebar_layout.addStretch()
        
        version_label = QLabel("v1.0")
        version_label.setStyleSheet("color: #5a5a7a; font-size: 11px;")
        version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version_label)
        
        main_layout.addWidget(sidebar)
        
        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(25, 20, 25, 20)
        content_layout.setSpacing(15)
        
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_scroll_page(self.create_organize_page()))
        self.pages.addWidget(self.create_scroll_page(self.create_filters_page()))
        self.pages.addWidget(self.create_scroll_page(self.create_tools_page()))
        content_layout.addWidget(self.pages)
        
        bottom_bar = QFrame()
        bottom_layout = QVBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(0, 10, 0, 0)
        bottom_layout.setSpacing(10)
        
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(25)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Listo")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setMinimumWidth(200)
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        progress_layout.addWidget(self.status_label)
        
        bottom_layout.addLayout(progress_layout)
        
        # Botones de acción principales
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        preview_btn = QPushButton("👁️ Vista Previa")
        preview_btn.clicked.connect(self.show_preview)
        action_layout.addWidget(preview_btn)
        
        execute_btn = QPushButton("▶️ Ejecutar")
        execute_btn.setObjectName("executeBtn")
        execute_btn.clicked.connect(self.execute_organization)
        action_layout.addWidget(execute_btn)
        
        reset_btn = QPushButton("🔄 Resetear")
        reset_btn.clicked.connect(self.reset_form)
        action_layout.addWidget(reset_btn)
        
        bottom_layout.addLayout(action_layout)
        
        content_layout.addWidget(bottom_bar)
        main_layout.addWidget(content_area)
    
    def create_organize_page(self):
        """Crea la página principal de organización."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("🗂️ Organizar Archivos")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Carpeta origen
        source_group = QGroupBox("Carpeta de Origen")
        source_layout = QHBoxLayout()
        self.source_path_input = QLineEdit()
        self.source_path_input.setPlaceholderText("Selecciona la carpeta a organizar...")
        self.source_path_input.setReadOnly(True)
        source_btn = QPushButton("📁 Seleccionar")
        source_btn.setFixedWidth(120)
        source_btn.clicked.connect(self.select_source_folder)
        source_layout.addWidget(self.source_path_input)
        source_layout.addWidget(source_btn)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # Categorías
        categories_group = QGroupBox("Tipos de Archivo")
        categories_layout = QGridLayout()
        categories_layout.setSpacing(10)
        
        self.category_checkboxes = {}
        row, col = 0, 0
        for category_name in EXTENSION_CATEGORIES.keys():
            checkbox = QCheckBox(category_name)
            checkbox.stateChanged.connect(self.update_rules_from_categories)
            self.category_checkboxes[category_name] = checkbox
            categories_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 4:
                col = 0
                row += 1
        
        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)
        
        # Extensiones personalizadas
        custom_group = QGroupBox("Extensiones Personalizadas")
        custom_layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.rule_input = QLineEdit()
        self.rule_input.setPlaceholderText("Escribe una extensión (ej: pdf, mp3, txt)")
        self.rule_input.returnPressed.connect(self.add_rule)
        add_btn = QPushButton("➕ Añadir")
        add_btn.setFixedWidth(100)
        add_btn.clicked.connect(self.add_rule)
        input_layout.addWidget(self.rule_input)
        input_layout.addWidget(add_btn)
        custom_layout.addLayout(input_layout)
        
        self.rules_list = QListWidget()
        self.rules_list.setMaximumHeight(70)
        self.rules_list.setFlow(QListWidget.LeftToRight)
        self.rules_list.setWrapping(True)
        self.rules_list.setSpacing(5)
        custom_layout.addWidget(self.rules_list)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        # Carpeta destino
        dest_group = QGroupBox("Carpeta de Destino")
        dest_layout = QHBoxLayout()
        self.dest_path_input = QLineEdit()
        self.dest_path_input.setPlaceholderText("Selecciona dónde guardar los archivos organizados...")
        self.dest_path_input.setReadOnly(True)
        dest_btn = QPushButton("📁 Seleccionar")
        dest_btn.setFixedWidth(120)
        dest_btn.clicked.connect(self.select_destination_folder)
        dest_layout.addWidget(self.dest_path_input)
        dest_layout.addWidget(dest_btn)
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        # Opciones
        options_group = QGroupBox("Opciones")
        options_layout = QHBoxLayout()
        options_layout.setSpacing(30)
        
        # Operación
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Operación:"))
        self.operation_combo = QComboBox()
        self.operation_combo.addItems(["Copiar", "Mover"])
        self.operation_combo.currentIndexChanged.connect(self.update_operation)
        self.operation_combo.setFixedWidth(120)
        op_layout.addWidget(self.operation_combo)
        options_layout.addLayout(op_layout)
        
        # Organizar por
        org_layout = QHBoxLayout()
        org_layout.addWidget(QLabel("Organizar por:"))
        self.organize_by_combo = QComboBox()
        self.organize_by_combo.addItems(["Extensión", "Fecha", "Tamaño"])
        self.organize_by_combo.currentIndexChanged.connect(self.update_organize_by)
        self.organize_by_combo.setFixedWidth(120)
        org_layout.addWidget(self.organize_by_combo)
        options_layout.addLayout(org_layout)
        
        # Recursivo
        self.recursive_checkbox = QCheckBox("Incluir subcarpetas")
        self.recursive_checkbox.stateChanged.connect(self.update_recursive)
        options_layout.addWidget(self.recursive_checkbox)
        
        options_layout.addStretch()
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        return page
    
    def create_filters_page(self):
        """Crea la página de filtros avanzados."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("🔍 Filtros Avanzados")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Filtro por nombre
        name_group = QGroupBox("Filtrar por Nombre")
        name_layout = QVBoxLayout()
        name_layout.setSpacing(15)
        
        include_layout = QHBoxLayout()
        include_layout.addWidget(QLabel("Incluir si contiene:"))
        self.name_filter_input = QLineEdit()
        self.name_filter_input.setPlaceholderText("Ej: IMG_, documento, backup")
        self.name_filter_input.textChanged.connect(self.update_name_filter)
        include_layout.addWidget(self.name_filter_input)
        name_layout.addLayout(include_layout)
        
        exclude_layout = QHBoxLayout()
        exclude_layout.addWidget(QLabel("Excluir si contiene:"))
        self.exclude_filter_input = QLineEdit()
        self.exclude_filter_input.setPlaceholderText("Ej: temp, cache, .bak")
        self.exclude_filter_input.textChanged.connect(self.update_exclude_filter)
        exclude_layout.addWidget(self.exclude_filter_input)
        name_layout.addLayout(exclude_layout)
        
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Filtro por tamaño
        size_group = QGroupBox("Filtrar por Tamaño")
        size_layout = QHBoxLayout()
        size_layout.setSpacing(20)
        
        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("Mínimo:"))
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 100000)
        self.min_size_spin.setSuffix(" MB")
        self.min_size_spin.setFixedWidth(120)
        self.min_size_spin.valueChanged.connect(self.update_size_filter)
        min_layout.addWidget(self.min_size_spin)
        size_layout.addLayout(min_layout)
        
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Máximo:"))
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(0, 100000)
        self.max_size_spin.setSuffix(" MB")
        self.max_size_spin.setSpecialValueText("Sin límite")
        self.max_size_spin.setFixedWidth(120)
        self.max_size_spin.valueChanged.connect(self.update_size_filter)
        max_layout.addWidget(self.max_size_spin)
        size_layout.addLayout(max_layout)
        
        size_layout.addStretch()
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Destinos personalizados
        custom_group = QGroupBox("Carpetas Personalizadas por Extensión")
        custom_layout = QVBoxLayout()
        
        custom_input = QHBoxLayout()
        custom_input.addWidget(QLabel("Extensión:"))
        self.custom_ext_input = QLineEdit()
        self.custom_ext_input.setPlaceholderText("pdf")
        self.custom_ext_input.setFixedWidth(80)
        custom_input.addWidget(self.custom_ext_input)
        
        custom_input.addWidget(QLabel("→ Carpeta:"))
        self.custom_folder_input = QLineEdit()
        self.custom_folder_input.setPlaceholderText("Mis PDFs")
        custom_input.addWidget(self.custom_folder_input)
        
        add_custom_btn = QPushButton("➕ Añadir")
        add_custom_btn.setFixedWidth(100)
        add_custom_btn.clicked.connect(self.add_custom_destination)
        custom_input.addWidget(add_custom_btn)
        
        custom_layout.addLayout(custom_input)
        
        self.custom_dest_list = QListWidget()
        self.custom_dest_list.setMaximumHeight(80)
        custom_layout.addWidget(self.custom_dest_list)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
        layout.addStretch()
        return page
    
    def create_tools_page(self):
        """Crea la página de herramientas."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("🛠️ Herramientas")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Duplicados
        dup_group = QGroupBox("Detector de Duplicados")
        dup_layout = QVBoxLayout()
        
        dup_info = QLabel("Encuentra archivos duplicados comparando su contenido (hash MD5).\nÚtil para liberar espacio eliminando copias innecesarias.")
        dup_info.setWordWrap(True)
        dup_info.setStyleSheet("color: #8a8aaa;")
        dup_layout.addWidget(dup_info)
        
        find_dup_btn = QPushButton("🔍 Buscar Duplicados")
        find_dup_btn.clicked.connect(self.find_duplicates)
        dup_layout.addWidget(find_dup_btn)
        
        dup_group.setLayout(dup_layout)
        layout.addWidget(dup_group)
        
        # Deshacer
        undo_group = QGroupBox("Deshacer Operaciones")
        undo_layout = QVBoxLayout()
        
        undo_info = QLabel("Restaura todos los archivos de la última operación de 'Mover' a su ubicación original.\nLas operaciones de 'Copiar' no se pueden deshacer.")
        undo_info.setWordWrap(True)
        undo_info.setStyleSheet("color: #8a8aaa;")
        undo_layout.addWidget(undo_info)
        
        undo_btns = QHBoxLayout()
        undo_btn = QPushButton("↩️ Deshacer Última Operación")
        undo_btn.clicked.connect(self.undo_last)
        undo_btns.addWidget(undo_btn)
        
        history_btn = QPushButton("📜 Ver Historial")
        history_btn.clicked.connect(self.show_history)
        undo_btns.addWidget(history_btn)
        
        undo_layout.addLayout(undo_btns)
        undo_group.setLayout(undo_layout)
        layout.addWidget(undo_group)
        
        # Info
        info_group = QGroupBox("Información")
        info_layout = QVBoxLayout()
        
        info_text = QLabel("""
<b>Consejos:</b><br>
• Usa <b>Vista Previa</b> antes de ejecutar para verificar los archivos<br>
• Las operaciones de <b>Mover</b> se pueden deshacer completamente<br>
• Los <b>duplicados</b> se detectan por contenido, no por nombre<br>
• Usa <b>filtros</b> para organizar solo archivos específicos
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #8a8aaa; line-height: 1.5;")
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        return page
    
    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)
    
    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta de origen")
        if folder:
            self.source_path_input.setText(folder)
            self.organizer.set_source_folder(folder)
    
    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta de destino")
        if folder:
            self.dest_path_input.setText(folder)
            self.organizer.set_destination_folder(folder)
    
    def add_rule(self):
        rule_text = self.rule_input.text().strip()
        if not rule_text:
            return
        
        if not rule_text.startswith('.'):
            rule_text = '.' + rule_text
        
        existing = [self.rules_list.item(i).text() for i in range(self.rules_list.count())]
        if rule_text not in existing:
            item = QListWidgetItem(rule_text)
            self.rules_list.addItem(item)
        
        self.rule_input.clear()
        self.update_rules_in_organizer()
    
    def update_rules_from_categories(self):
        self.rules_list.clear()
        
        for category_name, checkbox in self.category_checkboxes.items():
            if checkbox.isChecked():
                for ext in EXTENSION_CATEGORIES[category_name]:
                    existing = [self.rules_list.item(i).text() for i in range(self.rules_list.count())]
                    if ext not in existing:
                        self.rules_list.addItem(QListWidgetItem(ext))
        
        self.update_rules_in_organizer()
    
    def update_rules_in_organizer(self):
        rules = [self.rules_list.item(i).text() for i in range(self.rules_list.count())]
        self.organizer.set_rules(rules)
    
    def update_operation(self):
        self.organizer.set_operation("copy" if self.operation_combo.currentIndex() == 0 else "move")
    
    def update_organize_by(self):
        methods = ["extension", "date", "size"]
        self.organizer.set_organize_by(methods[self.organize_by_combo.currentIndex()])
    
    def update_recursive(self):
        self.organizer.set_recursive(self.recursive_checkbox.isChecked())
    
    def update_name_filter(self):
        self.organizer.set_name_filter(self.name_filter_input.text())
    
    def update_exclude_filter(self):
        self.organizer.set_exclude_filter(self.exclude_filter_input.text())
    
    def update_size_filter(self):
        min_size = self.min_size_spin.value() * 1024 * 1024
        max_size = self.max_size_spin.value() * 1024 * 1024 if self.max_size_spin.value() > 0 else None
        self.organizer.set_size_filter(min_size, max_size)
    
    def add_custom_destination(self):
        ext = self.custom_ext_input.text().strip()
        folder = self.custom_folder_input.text().strip()
        
        if ext and folder:
            if not ext.startswith('.'):
                ext = '.' + ext
            self.organizer.set_custom_destination(ext, folder)
            self.custom_dest_list.addItem(f"{ext} → {folder}")
            self.custom_ext_input.clear()
            self.custom_folder_input.clear()
    
    def show_preview(self):
        if not self.source_path_input.text():
            QMessageBox.warning(self, "Error", "Selecciona una carpeta de origen")
            return
        
        if self.rules_list.count() == 0:
            QMessageBox.warning(self, "Error", "Selecciona al menos un tipo de archivo")
            return
        
        self.status_label.setText("Escaneando...")
        self.progress_bar.setValue(0)
        
        self.worker = WorkerThread(self.organizer, "scan")
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.start()
    
    def on_scan_finished(self, success, message):
        self.status_label.setText(message)
        self.progress_bar.setValue(100)
        
        if success and self.organizer._preview_files:
            dialog = PreviewDialog(self.organizer.get_preview(), self)
            dialog.exec()
        elif not self.organizer._preview_files:
            QMessageBox.information(self, "Vista Previa", "No se encontraron archivos con los filtros seleccionados")
    
    def execute_organization(self):
        if not self.source_path_input.text():
            QMessageBox.warning(self, "Error", "Selecciona una carpeta de origen")
            return
        
        if not self.dest_path_input.text():
            QMessageBox.warning(self, "Error", "Selecciona una carpeta de destino")
            return
        
        if self.rules_list.count() == 0:
            QMessageBox.warning(self, "Error", "Selecciona al menos un tipo de archivo")
            return
        
        op_text = "mover" if self.organizer.operation == "move" else "copiar"
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Deseas {op_text} los archivos seleccionados?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.status_label.setText("Organizando...")
        self.progress_bar.setValue(0)
        
        self.worker = WorkerThread(self.organizer, "organize")
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_organize_finished)
        self.worker.start()
    
    def on_organize_finished(self, success, message):
        self.status_label.setText(message)
        self.progress_bar.setValue(100)
        
        results = self.organizer.get_results()
        
        result_msg = f"{message}\n\n"
        if results["copied"]:
            result_msg += f"✓ Copiados: {len(results['copied'])}\n"
        if results["moved"]:
            result_msg += f"✓ Movidos: {len(results['moved'])}\n"
        if results["errors"]:
            result_msg += f"\n✗ Errores: {len(results['errors'])}\n"
        
        QMessageBox.information(self, "Resultado", result_msg)
    
    def update_progress(self, current, total):
        if total > 0:
            self.progress_bar.setValue(int((current / total) * 100))
            self.status_label.setText(f"{current}/{total}")
    
    def undo_last(self):
        history = self.organizer.get_history(1)
        if not history:
            QMessageBox.information(self, "Deshacer", "No hay operaciones para deshacer")
            return
        
        last_batch = history[0]
        count = len(last_batch.get("operations", []))
        
        if last_batch["type"] != "move":
            QMessageBox.warning(self, "Deshacer", "Solo se pueden deshacer operaciones de 'Mover'")
            return
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Deseas restaurar {count} archivos a su ubicación original?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.status_label.setText("Deshaciendo...")
        self.progress_bar.setValue(0)
        
        self.worker = WorkerThread(self.organizer, "undo")
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_undo_finished)
        self.worker.start()
    
    def on_undo_finished(self, success, message):
        self.status_label.setText(message)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Deshacer", message)
    
    def find_duplicates(self):
        if not self.source_path_input.text():
            QMessageBox.warning(self, "Error", "Selecciona una carpeta de origen")
            return
        
        self.status_label.setText("Buscando duplicados...")
        self.progress_bar.setValue(0)
        
        # Escanear todos los archivos (sin filtro de extensiones)
        self.organizer._preview_files = []
        self.organizer.rules = []  # Temporalmente sin filtro
        self.organizer.get_files()
        
        if not self.organizer._preview_files:
            QMessageBox.information(self, "Duplicados", "No se encontraron archivos")
            self.update_rules_in_organizer()
            return
        
        self.worker = WorkerThread(self.organizer, "duplicates")
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_duplicates_finished)
        self.worker.start()
    
    def on_duplicates_finished(self, success, message):
        self.status_label.setText(message)
        self.progress_bar.setValue(100)
        self.update_rules_in_organizer()  # Restaurar filtros
        
        if self.organizer.duplicate_finder.duplicates:
            dialog = DuplicatesDialog(self.organizer.duplicate_finder.duplicates, self)
            dialog.exec()
        else:
            QMessageBox.information(self, "Duplicados", "No se encontraron archivos duplicados")
    
    def show_history(self):
        history = self.organizer.get_history(20)
        if history:
            dialog = HistoryDialog(history, self)
            dialog.exec()
        else:
            QMessageBox.information(self, "Historial", "No hay operaciones en el historial")
    
    def reset_form(self):
        reply = QMessageBox.question(
            self, "Confirmar",
            "¿Resetear toda la configuración?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.source_path_input.clear()
            self.dest_path_input.clear()
            self.rules_list.clear()
            self.rule_input.clear()
            self.operation_combo.setCurrentIndex(0)
            self.organize_by_combo.setCurrentIndex(0)
            self.recursive_checkbox.setChecked(False)
            self.name_filter_input.clear()
            self.exclude_filter_input.clear()
            self.min_size_spin.setValue(0)
            self.max_size_spin.setValue(0)
            self.custom_dest_list.clear()
            
            for checkbox in self.category_checkboxes.values():
                checkbox.setChecked(False)
            
            self.organizer = FileOrganizer()
            self.progress_bar.setValue(0)
            self.status_label.setText("Listo")
