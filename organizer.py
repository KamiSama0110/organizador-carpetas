from pathlib import Path
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import shutil
import hashlib
import json


EXTENSION_CATEGORIES = {
    "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff", ".raw", ".heic"],
    "Documentos": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Ejecutables": [".exe", ".msi", ".deb", ".rpm", ".AppImage", ".sh", ".bat", ".cmd"],
    "Código": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".rb", ".go", ".rs", ".ts"],
    "Fuentes": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
    "Diseño": [".psd", ".ai", ".xd", ".fig", ".sketch", ".blend", ".obj", ".fbx"],
    "Libros": [".epub", ".mobi", ".azw", ".azw3", ".fb2", ".djvu"],
}

SIZE_CATEGORIES = {
    "Pequeños (<1MB)": (0, 1024 * 1024),
    "Medianos (1MB-100MB)": (1024 * 1024, 100 * 1024 * 1024),
    "Grandes (100MB-1GB)": (100 * 1024 * 1024, 1024 * 1024 * 1024),
    "Muy grandes (>1GB)": (1024 * 1024 * 1024, float('inf')),
}


def get_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """Calcula el hash MD5 de un archivo."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_size_category(size: int) -> str:
    """Retorna la categoría de tamaño para un archivo."""
    for category, (min_size, max_size) in SIZE_CATEGORIES.items():
        if min_size <= size < max_size:
            return category
    return "Desconocido"


class FileInfo:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.extension = path.suffix.lower()
        self.size = path.stat().st_size
        self.modified_date = datetime.fromtimestamp(path.stat().st_mtime)
        self.size_category = get_size_category(self.size)
        self._hash = None
    
    @property
    def hash(self) -> str:
        if self._hash is None:
            self._hash = get_file_hash(self.path)
        return self._hash
    
    def get_size_formatted(self) -> str:
        """Retorna el tamaño formateado."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.2f} GB"
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización."""
        return {
            "path": str(self.path),
            "name": self.name,
            "extension": self.extension,
            "size": self.size,
            "size_formatted": self.get_size_formatted(),
            "modified_date": self.modified_date.isoformat(),
            "size_category": self.size_category
        }


class OrganizationHistory:
    def __init__(self, history_file: Path = None):
        self.history_file = history_file or Path.home() / ".organizer_history.json"
        self.batches = []
        self.load_history()
    
    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.batches = json.load(f)
            except:
                self.batches = []
    
    def save_history(self):
        self.batches = self.batches[-20:]
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.batches, f, indent=2, ensure_ascii=False)
    
    def start_batch(self, operation_type: str):
        self.batches.append({
            "type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "operations": []
        })
    
    def add_to_batch(self, source: str, destination: str):
        if self.batches:
            self.batches[-1]["operations"].append({
                "source": source,
                "destination": destination
            })
    
    def finish_batch(self):
        self.save_history()
    
    def get_last_batches(self, count: int = 10) -> List[dict]:
        return self.batches[-count:][::-1]
    
    def undo_last_batch(self, progress_callback=None) -> Tuple[bool, str]:
        if not self.batches:
            return False, "No hay operaciones para deshacer"
        
        last_batch = self.batches[-1]
        
        if last_batch["type"] != "move":
            return False, "Solo se pueden deshacer operaciones de mover"
        
        operations = last_batch["operations"]
        if not operations:
            self.batches.pop()
            self.save_history()
            return False, "El lote está vacío"
        
        restored = 0
        errors = 0
        total = len(operations)
        
        for i, op in enumerate(reversed(operations)):
            try:
                source = Path(op["source"])
                destination = Path(op["destination"])
                
                if destination.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(destination), str(source))
                    restored += 1
                else:
                    errors += 1
                
                if progress_callback:
                    progress_callback(i + 1, total)
            except Exception:
                errors += 1
        
        self.batches.pop()
        self.save_history()
        
        if errors > 0:
            return True, f"Restaurados: {restored} | Errores: {errors}"
        return True, f"Restaurados {restored} archivos correctamente"
    
    def clear_history(self):
        self.batches = []
        self.save_history()


class DuplicateFinder:
    def __init__(self):
        self.duplicates = {}
    
    def find_duplicates(self, files: List[FileInfo], progress_callback=None) -> Dict[str, List[FileInfo]]:
        self.duplicates = {}
        
        size_groups = {}
        for file_info in files:
            if file_info.size not in size_groups:
                size_groups[file_info.size] = []
            size_groups[file_info.size].append(file_info)
        
        total = len([f for files in size_groups.values() if len(files) > 1 for f in files])
        processed = 0
        
        for size, file_list in size_groups.items():
            if len(file_list) > 1:
                hash_groups = {}
                for file_info in file_list:
                    try:
                        file_hash = file_info.hash
                        if file_hash not in hash_groups:
                            hash_groups[file_hash] = []
                        hash_groups[file_hash].append(file_info)
                        
                        processed += 1
                        if progress_callback:
                            progress_callback(processed, total)
                    except Exception:
                        continue
                
                for file_hash, hash_files in hash_groups.items():
                    if len(hash_files) > 1:
                        self.duplicates[file_hash] = hash_files
        
        return self.duplicates
    
    def get_duplicate_count(self) -> int:
        return sum(len(files) - 1 for files in self.duplicates.values())
    
    def get_wasted_space(self) -> int:
        total = 0
        for files in self.duplicates.values():
            if files:
                total += files[0].size * (len(files) - 1)
        return total


class FileOrganizer:
    def __init__(self):
        self.source_folder = None
        self.destination_folder = None
        self.rules = []
        self.operation = "copy"
        self.recursive = False
        self.organize_by = "extension"
        self.name_filter = ""
        self.exclude_filter = ""
        self.min_size = 0
        self.max_size = float('inf')
        self.custom_destinations = {}
        
        self.history = OrganizationHistory()
        self.duplicate_finder = DuplicateFinder()
        
        self.results = {
            "moved": [],
            "copied": [],
            "errors": [],
            "skipped": []
        }
        
        self._preview_files = []
    
    def set_source_folder(self, folder_path: str) -> bool:
        path = Path(folder_path)
        if path.exists() and path.is_dir():
            self.source_folder = path
            return True
        return False
    
    def set_destination_folder(self, folder_path: str) -> bool:
        path = Path(folder_path)
        if path.exists() and path.is_dir():
            self.destination_folder = path
            return True
        return False
    
    def set_rules(self, rules: List[str]) -> None:
        self.rules = [rule if rule.startswith('.') else f'.{rule}' for rule in rules]
    
    def set_operation(self, operation: str) -> None:
        if operation in ["copy", "move"]:
            self.operation = operation
    
    def set_recursive(self, recursive: bool) -> None:
        self.recursive = recursive
    
    def set_organize_by(self, method: str) -> None:
        if method in ["extension", "date", "size"]:
            self.organize_by = method
    
    def set_name_filter(self, pattern: str) -> None:
        self.name_filter = pattern.lower()
    
    def set_exclude_filter(self, pattern: str) -> None:
        self.exclude_filter = pattern.lower()
    
    def set_size_filter(self, min_size: int = 0, max_size: int = None) -> None:
        self.min_size = min_size
        self.max_size = max_size if max_size else float('inf')
    
    def set_custom_destination(self, extension: str, folder_name: str) -> None:
        ext = extension if extension.startswith('.') else f'.{extension}'
        self.custom_destinations[ext] = folder_name
    
    def _matches_filters(self, file_info: FileInfo) -> bool:
        if self.rules and file_info.extension not in self.rules:
            return False
        
        if self.name_filter and self.name_filter not in file_info.name.lower():
            return False
        
        if self.exclude_filter and self.exclude_filter in file_info.name.lower():
            return False
        
        if not (self.min_size <= file_info.size <= self.max_size):
            return False
        
        return True
    
    def get_files(self, progress_callback=None) -> List[FileInfo]:
        if not self.source_folder:
            return []
        
        files = []
        pattern = self.source_folder.rglob('*') if self.recursive else self.source_folder.glob('*')
        
        all_files = [f for f in pattern if f.is_file()]
        total = len(all_files)
        
        for i, file_path in enumerate(all_files):
            try:
                file_info = FileInfo(file_path)
                if self._matches_filters(file_info):
                    files.append(file_info)
                
                if progress_callback:
                    progress_callback(i + 1, total)
            except Exception:
                continue
        
        self._preview_files = files
        return files
    
    def get_preview(self) -> List[dict]:
        return [f.to_dict() for f in self._preview_files]
    
    def find_duplicates(self, progress_callback=None) -> Dict[str, List[FileInfo]]:
        if not self._preview_files:
            self.get_files()
        return self.duplicate_finder.find_duplicates(self._preview_files, progress_callback)
    
    def _get_destination_folder_name(self, file_info: FileInfo) -> str:
        if file_info.extension in self.custom_destinations:
            return self.custom_destinations[file_info.extension]
        
        if self.organize_by == "extension":
            return file_info.extension.lstrip('.')
        elif self.organize_by == "date":
            return file_info.modified_date.strftime("%Y/%m")
        elif self.organize_by == "size":
            return file_info.size_category
        
        return file_info.extension.lstrip('.')
    
    def organize(self, progress_callback=None) -> Tuple[bool, str]:
        if not self.source_folder or not self.destination_folder:
            return False, "Error: Carpeta origen y destino son requeridas"
        
        self.results = {"moved": [], "copied": [], "errors": [], "skipped": []}
        
        if not self._preview_files:
            self.get_files()
        
        if not self._preview_files:
            return False, "No se encontraron archivos que coincidan con los filtros"
        
        total = len(self._preview_files)
        self.history.start_batch(self.operation)
        
        for i, file_info in enumerate(self._preview_files):
            try:
                folder_name = self._get_destination_folder_name(file_info)
                dest_folder = self.destination_folder / folder_name
                dest_folder.mkdir(parents=True, exist_ok=True)
                
                destination_path = dest_folder / file_info.name
                
                if destination_path.exists():
                    base = destination_path.stem
                    ext = destination_path.suffix
                    counter = 1
                    while destination_path.exists():
                        destination_path = dest_folder / f"{base}_{counter}{ext}"
                        counter += 1
                
                if self.operation == "move":
                    shutil.move(str(file_info.path), str(destination_path))
                    self.results["moved"].append(str(file_info.path))
                    self.history.add_to_batch(str(file_info.path), str(destination_path))
                else:
                    shutil.copy2(str(file_info.path), str(destination_path))
                    self.results["copied"].append(str(file_info.path))
                
                if progress_callback:
                    progress_callback(i + 1, total)
            
            except Exception as e:
                self.results["errors"].append(f"{file_info.name}: {str(e)}")
        
        self.history.finish_batch()
        
        total_processed = len(self.results["moved"]) + len(self.results["copied"])
        total_errors = len(self.results["errors"])
        
        message = f"Procesados: {total_processed} archivos"
        if total_errors > 0:
            message += f" | Errores: {total_errors}"
        
        return total_processed > 0, message
    
    def undo_last(self, progress_callback=None) -> Tuple[bool, str]:
        return self.history.undo_last_batch(progress_callback)
    
    def get_history(self, count: int = 10) -> List[dict]:
        return self.history.get_last_batches(count)
    
    def get_results(self) -> dict:
        return self.results
