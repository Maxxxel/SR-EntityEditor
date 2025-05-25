# drs_editor/gui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QDockWidget,
    QLabel,
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt, pyqtSlot
from drs_editor.file_handlers.drs_handler import DRSHandler
from .mesh_editor_tab import MeshEditorTab
from .log_widget import LogWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DRS Editor")
        self.setGeometry(100, 100, 800, 600)

        self.drs_handler = DRSHandler()
        self.current_drs_filepath = None

        # Central widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Tab widget for meshes
        self.mesh_tabs = QTabWidget()
        self.layout.addWidget(self.mesh_tabs)

        # Log widget
        self.log_widget = LogWidget()
        self.log_dock_widget = QDockWidget("Log", self)
        self.log_dock_widget.setWidget(self.log_widget)
        self.log_dock_widget.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock_widget)

        self.log_widget.log_message("DRS Editor initialized.")

        self._create_menus()

    def _create_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        load_action = QAction("&Load DRS...", self)
        load_action.setShortcut(QKeySequence.StandardKey.Open)
        load_action.triggered.connect(self.load_drs_file)
        file_menu.addAction(load_action)

        save_as_action = QAction("&Save DRS As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_drs_file_as)
        file_menu.addAction(save_as_action)

        # Add a status bar
        self.statusBar().showMessage("Ready")

    @pyqtSlot()
    def load_drs_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load DRS File", "", "DRS Files (*.drs)"
        )
        if filepath:
            self.log_widget.log_message(f"Attempting to load: {filepath}")
            success, message = self.drs_handler.load_drs(filepath)
            self.log_widget.log_message(message)
            # QMessageBox.information(self, "Load Status", message)
            if success:
                self.current_drs_filepath = filepath
                self.statusBar().showMessage(
                    f"Loaded: {filepath}. Model Type: {self.drs_handler.drs_object.model_type if self.drs_handler.drs_object else 'Unknown'}"
                )
                self.populate_mesh_tabs()
            else:
                self.current_drs_filepath = None
                self.statusBar().showMessage("Failed to load DRS file.")

    @pyqtSlot()
    def save_drs_file_as(self):
        if not self.drs_handler.drs_object:
            QMessageBox.warning(self, "Save Error", "No DRS file loaded to save.")
            self.log_widget.log_message("Save attempt failed: No DRS data.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save DRS File As...", "", "DRS Files (*.drs)"
        )
        if filepath:
            self.log_widget.log_message(f"Attempting to save to: {filepath}")
            # Before saving, ensure any changes in GUI are propagated to drs_handler.drs_object
            # And that node_sizes are updated via drs_handler.update_node_size(modified_object)
            # This is a placeholder for where GUI changes would be committed.
            # For V1, if we implement editors, they should call this.

            success, message = self.drs_handler.save_drs(filepath)
            self.log_widget.log_message(message)
            QMessageBox.information(self, "Save Status", message)
            if success:
                self.statusBar().showMessage(f"Saved to: {filepath}")
            else:
                self.statusBar().showMessage("Failed to save DRS file.")

    def populate_mesh_tabs(self):
        self.mesh_tabs.clear()
        battleforge_meshes = self.drs_handler.get_battleforge_meshes()
        if not battleforge_meshes:
            self.log_widget.log_message(
                "No meshes found in CDspMeshFile or CDspMeshFile not present."
            )
            # Display a message in the tab area if no meshes
            no_mesh_label = QLabel("No editable meshes found in the loaded DRS file.")
            no_mesh_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.mesh_tabs.addTab(no_mesh_label, "Info")
            return

        for i, bf_mesh in enumerate(battleforge_meshes):
            mesh_tab = MeshEditorTab(bf_mesh, self.drs_handler, self.log_widget)
            self.mesh_tabs.addTab(mesh_tab, f"Mesh {i+1}")
        self.log_widget.log_message(f"Populated {len(battleforge_meshes)} mesh tabs.")
