import os
import sys

os.environ["QT_API"] = "pyside6"

from PySide6.QtWidgets import QApplication

from gui import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()