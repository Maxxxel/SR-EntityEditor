# drs_editor/main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from .gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    # You can set a style here if you like
    app.setStyle("Fusion")

    # Create a font and set it for the application
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    main_win = MainWindow()
    main_win.show()
    return app.exec()


if __name__ == "__main__":
    # This allows running main.py directly for testing,
    # but run.py is the preferred entry point for a packaged app.
    # Adjust sys.path if run directly to find the drs_editor package
    import os

    if not __package__:  # If run directly
        # Calculate path to the parent directory (drs_editor_project)
        # and add it to sys.path to allow relative imports from drs_editor.
        package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sys.path.insert(0, package_path)
        from drs_editor.main import main as package_main

        sys.exit(package_main())
    else:  # If run as part of a package
        sys.exit(main())
