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
    QSizePolicy,  # Added
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt, pyqtSlot
from drs_editor.file_handlers.drs_handler import DRSHandler
from .mesh_editor_tab import MeshEditorTab
from .log_widget import LogWidget

# Placeholder for AnimationSet Editor
from .editors.animation_set_editor import (
    AnimationSetEditorWidget,
)  # We'll create this file


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DRS Editor")
        # Adjusted initial size for potentially more top-level tabs
        self.setGeometry(100, 100, 900, 700)

        self.drs_handler = DRSHandler()
        self.current_drs_filepath = None

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(
            self.central_widget
        )  # Renamed from self.layout for clarity
        self.setCentralWidget(self.central_widget)

        # --- Main Application Tab Widget ---
        self.app_tabs = QTabWidget()
        self.main_layout.addWidget(self.app_tabs)

        # Log widget (remains the same)
        self.log_widget = LogWidget()
        self.log_dock_widget = QDockWidget("Log", self)
        self.log_dock_widget.setWidget(self.log_widget)
        self.log_dock_widget.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock_widget)

        # --- Placeholder for Mesh Editing Area ---
        # This widget will contain the tab widget for individual meshes
        self.mesh_editor_area_widget = QWidget()
        self.mesh_editor_area_layout = QVBoxLayout(self.mesh_editor_area_widget)
        self.mesh_editor_area_layout.setContentsMargins(0, 0, 0, 0)
        self.mesh_details_tab_widget = (
            QTabWidget()
        )  # This will hold Mesh 1, Mesh 2, etc.
        self.mesh_editor_area_layout.addWidget(self.mesh_details_tab_widget)
        self.app_tabs.addTab(self.mesh_editor_area_widget, "Meshes")

        # --- Placeholder for AnimationSet Editing Area ---
        self.animation_set_editor_widget = AnimationSetEditorWidget(
            self.drs_handler, self.log_widget
        )
        self.app_tabs.addTab(self.animation_set_editor_widget, "AnimationSet")
        # Initially disable AnimationSet tab until a DRS is loaded
        self.app_tabs.setTabEnabled(
            self.app_tabs.indexOf(self.animation_set_editor_widget), False
        )

        self.log_widget.log_message("DRS Editor initialized.")
        self._create_menus()
        self.statusBar().showMessage("Ready")

    def _create_menus(self):  # Remains the same
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

    @pyqtSlot()
    def load_drs_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load DRS File", "", "DRS Files (*.drs)"
        )
        if filepath:
            self.log_widget.log_message(f"Attempting to load: {filepath}")
            # Clear previous data before loading new file
            self.clear_all_data_tabs()

            success, message = self.drs_handler.load_drs(filepath)
            self.log_widget.log_message(message)

            if success and self.drs_handler.drs_object:
                self.current_drs_filepath = filepath
                self.statusBar().showMessage(
                    f"Loaded: {filepath}. Model Type: {self.drs_handler.drs_object.model_type if self.drs_handler.drs_object else 'Unknown'}"
                )
                self.populate_mesh_detail_tabs()
                self.populate_animation_set_tab()  # New method
                # Enable AnimationSet tab
                self.app_tabs.setTabEnabled(
                    self.app_tabs.indexOf(self.animation_set_editor_widget), True
                )
            else:
                QMessageBox.warning(
                    self, "Load Error", message
                )  # Show error if load fails
                self.current_drs_filepath = None
                self.statusBar().showMessage("Failed to load DRS file.")
                # Disable AnimationSet tab if load failed or no object
                self.app_tabs.setTabEnabled(
                    self.app_tabs.indexOf(self.animation_set_editor_widget), False
                )

    def clear_all_data_tabs(self):
        """Clears content from all data-dependent tabs."""
        self.mesh_details_tab_widget.clear()
        # If AnimationSet editor has content to clear, do it here
        self.animation_set_editor_widget.clear_data()  # Add this method to AnimationSetEditorWidget
        # Add clearing for other future top-level tabs here

    def populate_mesh_detail_tabs(self):
        self.mesh_details_tab_widget.clear()  # Use the new nested tab widget
        battleforge_meshes = self.drs_handler.get_battleforge_meshes()
        if not battleforge_meshes:
            self.log_widget.log_message(
                "No meshes found in CDspMeshFile or CDspMeshFile not present."
            )
            no_mesh_label = QLabel("No editable meshes found in the loaded DRS file.")
            no_mesh_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.mesh_details_tab_widget.addTab(
                no_mesh_label, "Info"
            )  # Add to nested tab
            return

        for i, bf_mesh in enumerate(battleforge_meshes):
            mesh_tab_content = MeshEditorTab(bf_mesh, self.drs_handler, self.log_widget)
            self.mesh_details_tab_widget.addTab(
                mesh_tab_content, f"Mesh {i+1}"
            )  # Add to nested tab
        self.log_widget.log_message(
            f"Populated {len(battleforge_meshes)} mesh detail tabs."
        )

    def populate_animation_set_tab(self):
        """Populates the AnimationSet tab with data from the loaded DRS."""
        if (
            self.drs_handler
            and self.drs_handler.drs_object
            and hasattr(self.drs_handler.drs_object, "animation_set")
            and self.drs_handler.drs_object.animation_set is not None
        ):  #
            self.animation_set_editor_widget.set_data(
                self.drs_handler.drs_object.animation_set
            )  #
            self.log_widget.log_message("AnimationSet data loaded into tab.")
        else:
            self.animation_set_editor_widget.clear_data()
            self.log_widget.log_message(
                "No AnimationSet data found in DRS or DRS not loaded."
            )

    @pyqtSlot()
    def save_drs_file_as(self):  # Remains largely the same
        if not self.drs_handler.drs_object:
            QMessageBox.warning(self, "Save Error", "No DRS file loaded to save.")
            self.log_widget.log_message("Save attempt failed: No DRS data.")
            return

        # --- Important: Commit changes from UI to data objects before saving ---
        # This needs to be more robust. Iterate through active tabs and call a commit method.
        # For MeshEditorTab:
        for i in range(self.mesh_details_tab_widget.count()):
            widget = self.mesh_details_tab_widget.widget(i)
            if isinstance(widget, MeshEditorTab):
                widget.commit_changes()  # Ensure MeshEditorTab has this method to propagate

        # For AnimationSetEditorWidget:
        if hasattr(self.animation_set_editor_widget, "commit_changes"):
            self.animation_set_editor_widget.commit_changes()
        # --- End of commit changes ---

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save DRS File As...", "", "DRS Files (*.drs)"
        )
        if filepath:
            self.log_widget.log_message(f"Attempting to save to: {filepath}")
            success, message = self.drs_handler.save_drs(filepath)
            self.log_widget.log_message(message)
            QMessageBox.information(self, "Save Status", message)
            if success:
                self.statusBar().showMessage(f"Saved to: {filepath}")
            else:
                self.statusBar().showMessage("Failed to save DRS file.")
