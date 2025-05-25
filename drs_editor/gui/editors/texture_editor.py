# drs_editor/gui/editors/texture_editor.py
import os

# pylint: disable=no-name-in-module
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics

from drs_editor.data_structures.drs_definitions import Textures, Texture  #
from drs_editor.file_handlers.drs_handler import DRSHandler
from drs_editor.gui.log_widget import LogWidget
from .texture_preview_dialog import TexturePreviewDialog

TEXTURE_MAP_DEFINITIONS = {
    "Color Map": 1684432499,
    "Parameter Map": 1936745324,
    "Normal Map": 1852992883,
    "Environment Map": 1701738100,
    "Refraction Map": 1919116143,
    "Distortion Map": 1684628335,
    "Scratch Map": 1668510769,
    "Fluid Map": 1668510770,
}


class TextureSlotWidget(QWidget):
    def __init__(
        self,
        map_type_name: str,
        map_identifier: int,
        textures_obj: Textures,
        drs_handler: DRSHandler,
        log_widget: LogWidget,
        drs_file_dir: str | None,
        parent_mesh_object,
        parent=None,
    ):
        super().__init__(parent)
        self.map_type_name = map_type_name
        self.map_identifier = map_identifier
        self.textures_obj = textures_obj
        self.drs_handler = drs_handler
        self.log_widget = log_widget
        self.drs_file_dir = drs_file_dir
        self.parent_mesh_object = parent_mesh_object

        self.current_texture_object: Texture | None = None

        main_hbox = QHBoxLayout(self)
        main_hbox.setContentsMargins(2, 2, 2, 2)  # Reduced margins
        main_hbox.setSpacing(5)  # Reduced spacing between elements

        self.map_type_label = QLabel(f"{self.map_type_name}:")
        # Let map_type_label take its natural width, or set a fixed width if aligned look is needed
        self.map_type_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        self.name_display_label = QLabel("<i>None</i>")
        # Make it expand horizontally, but fixed or minimum vertically
        self.name_display_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        # self.name_display_label.setWordWrap(False) # Explicitly false, default anyway
        self.name_display_label.setFixedHeight(
            self.fontMetrics().height() + 2
        )  # Set to single line height + small padding

        self.preview_btn = QPushButton("...")  # Using "..." for very compact preview
        self.preview_btn.setToolTip("Preview Texture")
        self.preview_btn.setFixedSize(28, 28)  # Make buttons small and square-ish

        self.clear_btn = QPushButton("X")  # Using "X" for compact clear
        self.clear_btn.setToolTip("Clear Texture")
        self.clear_btn.setFixedSize(28, 28)
        self.clear_btn.setStyleSheet("QPushButton { color: red; font-weight: bold; }")

        self.load_btn = QPushButton("Load")
        self.load_btn.setToolTip("Load New Texture")
        self.load_btn.setFixedHeight(
            28
        )  # Match height of other buttons but allow width to vary for "Load" text
        # Or self.load_btn.setFixedSize(50,28)

        main_hbox.addWidget(self.map_type_label)
        main_hbox.addWidget(self.name_display_label)
        main_hbox.addWidget(self.preview_btn)
        main_hbox.addWidget(self.clear_btn)
        main_hbox.addWidget(self.load_btn)

        self.preview_btn.clicked.connect(self.preview_texture)
        self.load_btn.clicked.connect(self.load_texture)
        self.clear_btn.clicked.connect(self.clear_texture)

        self.update_display()

    def elide_text(self, text: str, max_width: int) -> str:
        metrics = QFontMetrics(self.name_display_label.font())
        return metrics.elidedText(text, Qt.TextElideMode.ElideRight, max_width)

    def update_display(self):
        self.current_texture_object = self.find_texture_object()
        full_path = self.get_full_texture_path()

        if self.current_texture_object:
            # Elide the text if it's too long for the available space in name_display_label
            # The max_width for eliding should ideally be the actual width of the label.
            # This is tricky to get before it's shown, so we might elide based on a reasonable guess
            # or update it in a resizeEvent. For now, just set the text.
            # A simpler approach for fixed height is that it just won't show if too long.
            display_name = self.current_texture_object.name
            # To make eliding effective, name_display_label needs a way to know its width for eliding
            # Or we set a maximum character length for display.
            # For now, we rely on setFixedHeight to clip it if it's too long.
            self.name_display_label.setText(display_name)
            self.name_display_label.setToolTip(
                f"Name: {display_name}\nPath: {full_path if full_path else 'N/A'}"
            )
            self.clear_btn.setEnabled(bool(full_path))
            # make the clear button "X" red if enabled else grey
            self.clear_btn.setStyleSheet(
                "QPushButton { color: red; font-weight: bold; }"
                if self.clear_btn.isEnabled()
                else "QPushButton { color: grey; }"
            )
            self.preview_btn.setEnabled(bool(full_path))
        else:
            self.name_display_label.setText("<i>None</i>")
            self.name_display_label.setToolTip("No texture assigned.")
            self.clear_btn.setEnabled(False)
            # make the clear button "X" grey
            self.clear_btn.setStyleSheet("QPushButton { color: grey; }")
            self.preview_btn.setEnabled(False)

    def get_full_texture_path(self) -> str | None:
        if (
            self.current_texture_object
            and self.drs_file_dir
            and self.current_texture_object.name
        ):
            texture_name = self.current_texture_object.name
            if "." not in texture_name:  # Assume .dds if no extension
                texture_name += ".dds"
            return os.path.join(self.drs_file_dir, texture_name)
        return None

    def find_texture_object(self) -> Texture | None:
        if not self.textures_obj or not self.textures_obj.textures:
            return None
        for tex in self.textures_obj.textures:
            if tex.identifier == self.map_identifier:
                return tex
        return None

    def preview_texture(self):
        full_path = self.get_full_texture_path()
        if full_path:
            self.log_widget.log_message(f"Opening preview for: {full_path}")
            preview_dialog = TexturePreviewDialog(full_path, self)
            preview_dialog.exec()  # Show as modal dialog
        else:
            self.log_widget.log_message(
                "Cannot preview: No texture loaded or DRS file path unknown."
            )

    def load_texture(self):
        if not self.drs_file_dir:
            self.log_widget.log_message(
                "Cannot load texture: DRS file directory is unknown."
            )
            # Potentially open a QMessageBox here
            return

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Texture File",
            self.drs_file_dir,
            "DDS Files (*.dds);;All Files (*)",  # Keep All Files for flexibility
        )
        if filepath:
            # Store name without extension
            base_name = os.path.splitext(os.path.basename(filepath))[0]

            old_name_log = "None"
            if (
                self.current_texture_object
            ):  # Existing texture for this slot is being replaced
                old_name_log = self.current_texture_object.name
                self.current_texture_object.name = base_name
                self.current_texture_object.length = len(base_name.encode("utf-8"))
            else:  # No texture in this slot, add a new one
                new_tex = Texture(identifier=self.map_identifier, name=base_name)
                new_tex.length = len(base_name.encode("utf-8"))  # Ensure length is set
                if not self.textures_obj.textures:  # Should always be a list
                    self.textures_obj.textures = []
                self.textures_obj.textures.append(new_tex)
                self.textures_obj.length = len(self.textures_obj.textures)

            self.log_widget.log_message(
                f"{self.map_type_name} assigned: '{base_name}' (was '{old_name_log}', ID: {self.map_identifier})"
            )
            self.update_display()
            if self.parent_mesh_object:
                self.drs_handler.update_node_size(self.parent_mesh_object)

    def clear_texture(self):
        if self.current_texture_object:
            removed_name = self.current_texture_object.name
            self.textures_obj.textures.remove(self.current_texture_object)
            self.textures_obj.length = len(self.textures_obj.textures)
            self.current_texture_object = None  # Important to reset this
            self.log_widget.log_message(
                f"{self.map_type_name} cleared (was '{removed_name}', ID: {self.map_identifier})"
            )
            self.update_display()
            if self.parent_mesh_object:
                self.drs_handler.update_node_size(self.parent_mesh_object)


class TextureEditorWidget(QGroupBox):
    def __init__(
        self,
        textures_obj: Textures,
        drs_handler: DRSHandler,
        log_widget: LogWidget,
        parent_mesh_object,  # This is the BattleforgeMesh
        parent=None,
    ):
        super().__init__("Texture Maps", parent)  #
        self.textures_obj = textures_obj  #
        self.drs_handler = drs_handler  #
        self.log_widget = log_widget  #
        self.parent_mesh_object = parent_mesh_object  #

        self.drs_file_dir = None  #
        if self.drs_handler.filepath:  #
            self.drs_file_dir = os.path.dirname(self.drs_handler.filepath)  #

        self.main_layout = QVBoxLayout(self)  #
        self.main_layout.setContentsMargins(
            5, 8, 5, 8
        )  # Add some padding inside the groupbox
        self.main_layout.setSpacing(3)  # Reduce spacing between texture slots

        if not self.textures_obj:  #
            self.main_layout.addWidget(  #
                QLabel("Texture data structure (Textures object) is missing.")
            )
            return  #

        for map_name, map_id in TEXTURE_MAP_DEFINITIONS.items():  #
            slot_widget = TextureSlotWidget(  #
                map_name,
                map_id,
                self.textures_obj,
                self.drs_handler,
                self.log_widget,
                self.drs_file_dir,
                self.parent_mesh_object,
            )
            self.main_layout.addWidget(slot_widget)  #

        self.main_layout.addStretch(1)  # Push all slots to the top
