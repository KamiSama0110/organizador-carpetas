"""
Punto de entrada de la aplicación.
"""

import sys
from PySide6.QtWidgets import QApplication
from ui import OrganizerWindow


def main():
    app = QApplication(sys.argv)
    window = OrganizerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
