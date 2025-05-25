# drs_editor/gui/editors/refraction_editor.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QFormLayout,
    QGroupBox,
)
from drs_editor.data_structures.drs_definitions import Refraction  #
from drs_editor.file_handlers.drs_handler import DRSHandler
from drs_editor.gui.log_widget import LogWidget


class RefractionEditorWidget(QGroupBox):
    def __init__(
        self,
        refraction_obj: Refraction,
        drs_handler: DRSHandler,
        log_widget: LogWidget,
        parent=None,
    ):
        super().__init__("Refraction", parent)
        self.refraction_obj = refraction_obj
        self.drs_handler = drs_handler
        self.log_widget = log_widget

        self.layout = QFormLayout(self)

        if (
            self.refraction_obj and self.refraction_obj.length == 1
        ):  # Only edit if length is 1 as per V1 scope
            self.layout.addRow(
                QLabel("Identifier:"), QLabel(str(self.refraction_obj.identifier))
            )  #

            self.r_edit = QLineEdit(str(self.refraction_obj.rgb[0]))  #
            self.g_edit = QLineEdit(str(self.refraction_obj.rgb[1]))  #
            self.b_edit = QLineEdit(str(self.refraction_obj.rgb[2]))  #

            self.r_edit.editingFinished.connect(
                lambda: self.update_rgb_comp(0, self.r_edit.text())
            )
            self.g_edit.editingFinished.connect(
                lambda: self.update_rgb_comp(1, self.g_edit.text())
            )
            self.b_edit.editingFinished.connect(
                lambda: self.update_rgb_comp(2, self.b_edit.text())
            )

            self.layout.addRow("Red:", self.r_edit)
            self.layout.addRow("Green:", self.g_edit)
            self.layout.addRow("Blue:", self.b_edit)
        elif self.refraction_obj and self.refraction_obj.length > 1:  #
            self.layout.addRow(
                QLabel(
                    "Refraction data has multiple entries. Editing not yet supported for this case."
                )
            )
        else:
            self.layout.addRow(
                QLabel(
                    "Refraction parameters not applicable or not loaded (length != 1)."
                )
            )

    def update_rgb_comp(self, index: int, value_str: str):
        comp_map = {0: "Red", 1: "Green", 2: "Blue"}
        try:
            new_val = float(value_str)
            # Add validation for 0.0-1.0 range if applicable for colors
            if not (0.0 <= new_val <= 255.0):  # Assuming 0-255, or 0-1 if normalized
                # For now, no strict range, but colors are often 0-1 or 0-255
                pass  # self.log_widget.log_message(f"Warning: Refraction {comp_map[index]} value {new_val} might be out of typical range (0-1 or 0-255).")

            old_val = self.refraction_obj.rgb[index]
            if old_val != new_val:
                self.refraction_obj.rgb[index] = new_val
                self.log_widget.log_message(
                    f"Refraction color {comp_map[index]} changed: {old_val} -> {new_val}"
                )
                # self.drs_handler.update_node_size(self.parent_mesh_object) # Propagate
        except ValueError:
            self.log_widget.log_message(
                f"Invalid float value for Refraction {comp_map[index]}: {value_str}"
            )
            # Revert QLineEdit text
