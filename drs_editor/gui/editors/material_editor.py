# In drs_editor/gui/editors/material_editor.py

from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QCheckBox,
    QWidget,
    QLabel,
    QScrollArea,
    QFormLayout,
    QLineEdit,
)
from PyQt6.QtCore import Qt
from drs_editor.data_structures.drs_definitions import BattleforgeMesh
from drs_editor.file_handlers.drs_handler import DRSHandler
from drs_editor.gui.log_widget import LogWidget
import math  # For math.log2

KNOWN_MATERIAL_FLAGS = {
    0: "Enable Alpha Test",
    1: "Decal Mode",
    2: "Unknown Bitflag #3",
    3: "Unknown Bitflag #4",
    4: "Unknown Bitflag #5",
    5: "Unknown Bitflag #6",
    6: "Unknown Bitflag #7",
    7: "Unknown Bitflag #8",
    8: "Unknown Bitflag #9",
    9: "Unknown Bitflag #10",
    10: "Unknown Bitflag #11",
    11: "Unknown Bitflag #12",
    12: "Unknown Bitflag #13",
    13: "Unknown Bitflag #14",
    14: "Unknown Bitflag #15",
    15: "Unknown Bitflag #16",
    16: "Use Parameter Map",
    17: "Use Normal Map",
    18: "Use Environment Map",
    19: "Unknown Bitflag #20",
    20: "Disable Receive Shadows",
    21: "Enable SH Lighting",
    22: "Unknown Bitflag #23",
    23: "Unknown Bitflag #24",
    24: "Unknown Bitflag #25",
    25: "Unknown Bitflag #26",
    26: "Unknown Bitflag #27",
    27: "Unknown Bitflag #28",
    28: "Unknown Bitflag #29",
    29: "Unknown Bitflag #30",
    30: "Unknown Bitflag #31",
    31: "Unknown Bitflag #32",
}


class MaterialEditorWidget(QGroupBox):
    def __init__(
        self,
        battleforge_mesh: BattleforgeMesh,
        drs_handler: DRSHandler,
        log_widget: LogWidget,
        parent=None,
    ):
        super().__init__("Material Flags (bool_parameter)", parent)
        self.battleforge_mesh = battleforge_mesh
        self.drs_handler = drs_handler
        self.log_widget = log_widget
        self.checkboxes: list[QCheckBox] = []
        self.max_relevant_bit_to_display = 0

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(5)

        raw_value_layout = QFormLayout()
        self.raw_bool_parameter_edit = QLineEdit()
        self.raw_bool_parameter_edit.setToolTip(
            "Raw integer value of bool_parameter. Changes here will update checkboxes, and vice-versa."
        )
        self.raw_bool_parameter_edit.editingFinished.connect(self.raw_value_changed)
        raw_value_layout.addRow(
            "Raw bool_parameter Value:", self.raw_bool_parameter_edit
        )
        self.main_layout.addLayout(raw_value_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        self.main_layout.addWidget(scroll_area)

        checkbox_container_widget = QWidget()
        self.checkbox_layout = QVBoxLayout(checkbox_container_widget)
        self.checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(checkbox_container_widget)

        self.refresh_ui()  # Initial population and update

    def refresh_ui(self):
        """Determines max bits, populates checkboxes, and updates UI from bool_parameter."""
        self.determine_max_relevant_bit()
        self.populate_flag_checkboxes()  # This now clears and repopulates
        self.update_ui_from_bool_parameter()  # This updates the states

    def determine_max_relevant_bit(self):
        current_bool_parameter = self.battleforge_mesh.bool_parameter
        highest_set_bit = -1
        if current_bool_parameter > 0:
            highest_set_bit = math.floor(math.log2(current_bool_parameter))

        highest_known_flag_bit = -1
        if KNOWN_MATERIAL_FLAGS:
            highest_known_flag_bit = max(KNOWN_MATERIAL_FLAGS.keys())

        self.max_relevant_bit_to_display = max(highest_set_bit, highest_known_flag_bit)

        # Default to showing a minimum number of bits if nothing significant is found
        # For example, if bool_parameter is 0 and KNOWN_MATERIAL_FLAGS is empty or only has low bits.
        # Ensure we at least show up to bit 7 (8 bits) or the highest known, whichever is greater.
        default_min_bits_to_show = 7  # Show bits 0-7
        self.max_relevant_bit_to_display = max(
            self.max_relevant_bit_to_display, default_min_bits_to_show
        )

        # Cap at 31 (for a 32-bit integer, bits 0-31)
        if self.max_relevant_bit_to_display > 31:
            self.max_relevant_bit_to_display = 31

    def populate_flag_checkboxes(self):
        for i in reversed(range(self.checkbox_layout.count())):
            item = self.checkbox_layout.itemAt(i)
            if item:  # Check if item is not None
                widget_to_remove = item.widget()
                if widget_to_remove:
                    widget_to_remove.deleteLater()
                else:  # If it's a layout, clear it and remove
                    layout_to_remove = item.layout()
                    if layout_to_remove:
                        # Recursively delete widgets in the layout
                        while layout_to_remove.count():
                            child = layout_to_remove.takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        # Remove the layout itself - this might not be directly possible,
                        # but clearing its contents is the main goal.
        self.checkboxes.clear()

        current_bool_parameter = self.battleforge_mesh.bool_parameter

        for bit_pos in range(self.max_relevant_bit_to_display + 1):
            label_text = KNOWN_MATERIAL_FLAGS.get(bit_pos)
            if label_text is None:
                # Dynamic generation if not in our predefined KNOWN_MATERIAL_FLAGS
                label_text = f"Unknown Bitflag #{bit_pos + 1}"  # 1-indexed for display

            checkbox = QCheckBox(f"{label_text} (Bit {bit_pos})")
            checkbox.setProperty("bit_position", bit_pos)
            checkbox.stateChanged.connect(self.checkbox_state_changed)
            self.checkboxes.append(checkbox)
            self.checkbox_layout.addWidget(checkbox)

        # Remove the note about displaying flags up to a certain bit,
        # as we are now trying to be more comprehensive up to max_relevant_bit.
        # Or, keep it if max_relevant_bit_to_display is still less than 31.
        if self.max_relevant_bit_to_display < 31:
            note_label = QLabel(
                f"<i>Displaying flags up to bit {self.max_relevant_bit_to_display}. Higher set bits are included in the raw value.</i>"
            )
            note_label.setWordWrap(True)
            self.checkbox_layout.addWidget(note_label)

    def update_ui_from_bool_parameter(self):
        current_bool_parameter = self.battleforge_mesh.bool_parameter
        # Block signals on raw_bool_parameter_edit while updating it to prevent re-triggering raw_value_changed
        self.raw_bool_parameter_edit.blockSignals(True)
        self.raw_bool_parameter_edit.setText(str(current_bool_parameter))
        self.raw_bool_parameter_edit.blockSignals(False)

        for checkbox in self.checkboxes:
            bit_pos = checkbox.property("bit_position")
            if bit_pos is not None:
                flag_value = 1 << bit_pos
                is_checked = (current_bool_parameter & flag_value) != 0
                checkbox.blockSignals(True)
                checkbox.setChecked(is_checked)
                checkbox.blockSignals(False)

    def checkbox_state_changed(self):
        new_bool_parameter = 0
        changed_checkbox: QCheckBox = self.sender()

        if not isinstance(changed_checkbox, QCheckBox):
            return

        bit_pos_changed = changed_checkbox.property("bit_position")
        flag_name = changed_checkbox.text().split(" (Bit")[0]

        # Reconstruct the bool_parameter from ALL current checkboxes
        for checkbox in self.checkboxes:
            bit_pos = checkbox.property("bit_position")
            if bit_pos is not None and checkbox.isChecked():
                new_bool_parameter |= 1 << bit_pos

        # Important: If there are bits set in the original bool_parameter that are
        # HIGHER than self.max_relevant_bit_to_display, they will be cleared by the above loop.
        # To preserve them:
        mask_for_higher_bits = 0
        if self.max_relevant_bit_to_display < 31:
            # Create a mask for all bits from (max_relevant_bit_to_display + 1) up to 31
            for i in range(self.max_relevant_bit_to_display + 1, 32):
                mask_for_higher_bits |= 1 << i

        higher_bits_value = self.battleforge_mesh.bool_parameter & mask_for_higher_bits
        new_bool_parameter |= higher_bits_value  # Add back the preserved higher bits

        if self.battleforge_mesh.bool_parameter != new_bool_parameter:
            old_value = self.battleforge_mesh.bool_parameter
            self.battleforge_mesh.bool_parameter = new_bool_parameter
            self.log_widget.log_message(
                f"Material Flag '{flag_name}' (Bit {bit_pos_changed}) changed to {changed_checkbox.isChecked()}. "
                f"bool_parameter: {old_value} -> {new_bool_parameter}"
            )
            # self.drs_handler.update_node_size(self.battleforge_mesh) # bool_parameter change doesn't change size

            # Update the raw value QLineEdit (blocking signals to prevent loop)
            self.raw_bool_parameter_edit.blockSignals(True)
            self.raw_bool_parameter_edit.setText(str(new_bool_parameter))
            self.raw_bool_parameter_edit.blockSignals(False)

    def raw_value_changed(self):
        try:
            new_value_int = int(self.raw_bool_parameter_edit.text())
            if new_value_int < 0:  # Or check against (1 << 32) if it's unsigned 32-bit
                self.log_widget.log_message(
                    "bool_parameter cannot be negative. Reverting."
                )
                self.raw_bool_parameter_edit.setText(
                    str(self.battleforge_mesh.bool_parameter)
                )
                return

            if self.battleforge_mesh.bool_parameter != new_value_int:
                old_value = self.battleforge_mesh.bool_parameter
                self.battleforge_mesh.bool_parameter = new_value_int
                self.log_widget.log_message(
                    f"Raw bool_parameter changed: {old_value} -> {new_value_int}"
                )
                # self.drs_handler.update_node_size(self.battleforge_mesh) # bool_parameter change doesn't change size

                # When raw value changes, re-evaluate displayed bits and update all UI elements
                self.refresh_ui()

        except ValueError:
            self.log_widget.log_message(
                f"Invalid integer for bool_parameter: {self.raw_bool_parameter_edit.text()}"
            )
            self.raw_bool_parameter_edit.setText(
                str(self.battleforge_mesh.bool_parameter)
            )
