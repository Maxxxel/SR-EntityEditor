# drs_editor/gui/editors/animation_set_editor.py
import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
    QComboBox,
    QSplitter,  # Added
    QListWidget,  # Added
    QListWidgetItem,  # Added
    QSizePolicy,  # Added
)
from PyQt6.QtCore import Qt
from drs_editor.data_structures.drs_definitions import (
    AnimationSet,
    ModeAnimationKey,
    AnimationSetVariant,
    AnimationType as DRSAnimationType,  # Renamed to avoid conflict if any
)
from drs_editor.file_handlers.drs_handler import DRSHandler
from drs_editor.gui.log_widget import LogWidget
from drs_editor.gui.vis_job_data import (
    VIS_JOB_MAP,
)  # Assuming this is defined in vis_job_data.py


class AnimationSetVariantWidget(QGroupBox):
    def __init__(
        self,
        variant: AnimationSetVariant,
        # anim_set: AnimationSet, # No longer directly needed by variant widget if it's self-contained
        drs_handler: DRSHandler,  # May not be needed if variant changes are local until commit
        log_widget: LogWidget,
        parent=None,
    ):
        super().__init__(
            f"Variant: {variant.file if variant.file else 'New Variant'}", parent
        )
        self.variant = variant
        # self.anim_set = anim_set
        self.drs_handler = drs_handler
        self.log_widget = log_widget

        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.ska_file_edit = QLineEdit(self.variant.file)
        self.ska_file_edit.editingFinished.connect(self.update_ska_file)
        self.layout.addRow("SKA File:", self.ska_file_edit)

        self.weight_spin = QSpinBox()
        self.weight_spin.setRange(0, 1000)
        self.weight_spin.setValue(self.variant.weight)
        self.weight_spin.valueChanged.connect(self.update_weight)
        self.layout.addRow("Weight:", self.weight_spin)

        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(0.0, 1000.0)  # Assuming max duration
        self.start_spin.setDecimals(3)
        self.start_spin.setValue(self.variant.start)
        self.start_spin.valueChanged.connect(self.update_start)
        self.layout.addRow("Start:", self.start_spin)

        self.end_spin = QDoubleSpinBox()
        self.end_spin.setRange(0.0, 1000.0)  # Assuming max duration
        self.end_spin.setDecimals(3)
        self.end_spin.setValue(self.variant.end)
        self.end_spin.valueChanged.connect(self.update_end)
        self.layout.addRow("End:", self.end_spin)

        self.allows_ik_check = QCheckBox()
        self.allows_ik_check.setChecked(bool(self.variant.allows_ik))
        self.allows_ik_check.stateChanged.connect(self.update_allows_ik)
        self.layout.addRow("Allows IK:", self.allows_ik_check)

        self.force_no_blend_check = QCheckBox()
        self.force_no_blend_check.setChecked(bool(self.variant.forceNoBlend))
        self.force_no_blend_check.stateChanged.connect(self.update_force_no_blend)
        self.layout.addRow("Force No Blend:", self.force_no_blend_check)

        self.update_field_visibility()

        self.edit_ska_button = QPushButton("Edit SKA (NYI)")
        self.edit_ska_button.clicked.connect(self.open_ska_editor)
        self.layout.addRow(self.edit_ska_button)
        self.edit_ska_button.setToolTip(
            "Open SKA Editor for this animation - Not Yet Implemented"
        )

    def update_variant_data(self, variant: AnimationSetVariant):
        """Updates the widget to display data from a new variant object."""
        self.variant = variant
        self.setTitle(
            f"Variant: {self.variant.file if self.variant.file else 'New Variant'}"
        )

        # Block signals while updating UI
        self.ska_file_edit.blockSignals(True)
        self.weight_spin.blockSignals(True)
        self.start_spin.blockSignals(True)
        self.end_spin.blockSignals(True)
        self.allows_ik_check.blockSignals(True)
        self.force_no_blend_check.blockSignals(True)

        self.ska_file_edit.setText(self.variant.file)
        self.weight_spin.setValue(self.variant.weight)
        self.start_spin.setValue(self.variant.start)
        self.end_spin.setValue(self.variant.end)
        self.allows_ik_check.setChecked(bool(self.variant.allows_ik))
        self.force_no_blend_check.setChecked(bool(self.variant.forceNoBlend))

        self.ska_file_edit.blockSignals(False)
        self.weight_spin.blockSignals(False)
        self.start_spin.blockSignals(False)
        self.end_spin.blockSignals(False)
        self.allows_ik_check.blockSignals(False)
        self.force_no_blend_check.blockSignals(False)

        self.update_field_visibility()

    def update_field_visibility(self):
        # This method should be called whenever variant.version might change,
        # or when the widget is first populated.
        if not hasattr(self.variant, "version"):  # Should always have it
            return

        version = self.variant.version
        form_layout = self.layout

        # Ensure labels are correctly accessed and their visibility toggled
        start_label = form_layout.labelForField(self.start_spin)
        if start_label:
            start_label.setVisible(version >= 4)
        self.start_spin.setVisible(version >= 4)

        end_label = form_layout.labelForField(self.end_spin)
        if end_label:
            end_label.setVisible(version >= 4)
        self.end_spin.setVisible(version >= 4)

        allows_ik_label = form_layout.labelForField(self.allows_ik_check)
        if allows_ik_label:
            allows_ik_label.setVisible(version >= 5)
        self.allows_ik_check.setVisible(version >= 5)

        force_no_blend_label = form_layout.labelForField(self.force_no_blend_check)
        if force_no_blend_label:
            force_no_blend_label.setVisible(version >= 7)
        self.force_no_blend_check.setVisible(version >= 7)

    def update_ska_file(self):
        new_file = self.ska_file_edit.text()
        if self.variant.file != new_file:
            self.variant.file = new_file
            self.variant.length = len(
                new_file.encode("utf-8")
            )  # Ensure length is updated
            self.setTitle(f"Variant: {new_file if new_file else 'Untitled'}")
            self.log_widget.log_message(f"Variant SKA file changed to: {new_file}")
            # TODO: Update the display name in the parent QListWidget (Middle Panel)

    def update_weight(self, value):
        self.variant.weight = value

    def update_start(self, value):
        self.variant.start = value

    def update_end(self, value):
        self.variant.end = value

    def update_allows_ik(self, state):
        self.variant.allows_ik = 1 if state == Qt.CheckState.Checked.value else 0

    def update_force_no_blend(self, state):
        self.variant.forceNoBlend = 1 if state == Qt.CheckState.Checked.value else 0

    def open_ska_editor(self):
        # ... (SKA editor logic remains the same) ...
        self.log_widget.log_message(
            f"Attempting to open SKA editor for: {self.variant.file} (Not Yet Implemented)"
        )
        ska_file_path = ""
        if self.drs_handler.filepath and self.variant.file:
            base_dir = os.path.dirname(self.drs_handler.filepath)
            # Construct path more robustly, assuming variant.file might or might not have .ska
            base_ska_name = self.variant.file
            if not base_ska_name.lower().endswith(".ska"):
                base_ska_name += ".ska"

            potential_path = os.path.join(base_dir, base_ska_name)

            if not os.path.exists(potential_path) and not os.path.isabs(
                self.variant.file
            ):
                # Try common subdirectories if not found directly and not absolute
                common_subdirs = [
                    "../anim",
                    "../animations",
                    "../ska",
                    "anim",
                    "animations",
                    "ska",
                ]
                for subdir in common_subdirs:
                    test_path = os.path.join(base_dir, subdir, base_ska_name)
                    if os.path.exists(test_path):
                        potential_path = test_path
                        break

            if os.path.exists(potential_path):
                ska_file_path = potential_path
                QMessageBox.information(
                    self,
                    "SKA Editor",
                    f"SKA Editor for {ska_file_path} would open here (NYI).",
                )
            else:
                QMessageBox.warning(
                    self,
                    "SKA File Not Found",
                    f"Could not find SKA file: {base_ska_name}\nSearched near: {os.path.dirname(potential_path)}",
                )
        else:
            QMessageBox.warning(
                self, "SKA File", "SKA filename or DRS path is not set."
            )


class AnimationSetEditorWidget(QWidget):
    def __init__(self, drs_handler: DRSHandler, log_widget: LogWidget, parent=None):
        super().__init__(parent)
        self.drs_handler = drs_handler
        self.log_widget = log_widget
        self.animation_set_data: AnimationSet | None = None
        self.current_mode_key: ModeAnimationKey | None = None
        self.current_variant: AnimationSetVariant | None = None

        self.main_layout = QVBoxLayout(self)

        # --- Top Section: General AnimationSet Properties ---
        top_props_container = QWidget()
        top_props_layout = QHBoxLayout(top_props_container)
        top_props_layout.setContentsMargins(0, 0, 0, 0)

        general_props_group = QGroupBox("General Properties")
        self.general_props_layout = QFormLayout()
        general_props_group.setLayout(self.general_props_layout)
        top_props_layout.addWidget(general_props_group)

        self.conditional_props_group = QGroupBox("Conditional Properties")
        self.conditional_props_layout = QFormLayout()
        self.conditional_props_group.setLayout(self.conditional_props_layout)
        top_props_layout.addWidget(self.conditional_props_group)

        self.main_layout.addWidget(top_props_container)

        # Populate General Properties fields
        self.version_spin = QSpinBox()
        self.version_spin.setRange(2, 7)
        self.general_props_layout.addRow("Version:", self.version_spin)
        self.revision_spin = QSpinBox()
        self.revision_spin.setRange(0, 10)
        self.general_props_layout.addRow("Revision:", self.revision_spin)
        self.run_speed_spin = QDoubleSpinBox()
        self.run_speed_spin.setDecimals(3)
        self.run_speed_spin.setRange(0.0, 100.0)
        self.general_props_layout.addRow("Default Run Speed:", self.run_speed_spin)
        self.walk_speed_spin = QDoubleSpinBox()
        self.walk_speed_spin.setDecimals(3)
        self.walk_speed_spin.setRange(0.0, 100.0)
        self.general_props_layout.addRow("Default Walk Speed:", self.walk_speed_spin)

        # Populate Conditional Properties fields
        self.mode_change_type_spin = QSpinBox()
        self.mode_change_type_spin.setRange(0, 255)
        self.conditional_props_layout.addRow(
            "Mode Change Type:", self.mode_change_type_spin
        )
        self.hovering_ground_check = QCheckBox("Hovering Ground")
        self.conditional_props_layout.addRow(self.hovering_ground_check)
        self.fly_bank_scale_spin = QDoubleSpinBox()
        self.fly_bank_scale_spin.setDecimals(3)
        self.fly_bank_scale_spin.setRange(-100.0, 100.0)
        self.conditional_props_layout.addRow(
            "Fly Bank Scale:", self.fly_bank_scale_spin
        )
        self.fly_accel_scale_spin = QDoubleSpinBox()
        self.fly_accel_scale_spin.setDecimals(3)
        self.fly_accel_scale_spin.setRange(-100.0, 100.0)
        self.conditional_props_layout.addRow(
            "Fly Accel Scale:", self.fly_accel_scale_spin
        )
        self.fly_hit_scale_spin = QDoubleSpinBox()
        self.fly_hit_scale_spin.setDecimals(3)
        self.fly_hit_scale_spin.setRange(-100.0, 100.0)
        self.conditional_props_layout.addRow("Fly Hit Scale:", self.fly_hit_scale_spin)
        self.align_to_terrain_check = QCheckBox("Align to Terrain")
        self.conditional_props_layout.addRow(self.align_to_terrain_check)

        # --- Main Three-Panel Area ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)  # Add with stretch factor

        # Left Panel: ModeAnimationKey List
        left_panel_widget = QWidget()
        left_panel_layout = QVBoxLayout(left_panel_widget)
        left_panel_layout.addWidget(QLabel("<b>Mode Keys</b>"))
        self.mode_keys_list_widget = QListWidget()
        self.mode_keys_list_widget.currentItemChanged.connect(self.on_mode_key_selected)
        left_panel_layout.addWidget(self.mode_keys_list_widget)
        key_buttons_layout = QHBoxLayout()
        add_key_button = QPushButton("Add Key")
        add_key_button.clicked.connect(self.add_mode_animation_key)
        remove_key_button = QPushButton("Remove Key")
        remove_key_button.clicked.connect(self.remove_mode_animation_key)
        key_buttons_layout.addWidget(add_key_button)
        key_buttons_layout.addWidget(remove_key_button)
        left_panel_layout.addLayout(key_buttons_layout)
        self.splitter.addWidget(left_panel_widget)

        # Middle Panel: ModeAnimationKey Details & Variant List
        middle_panel_widget = QWidget()
        middle_panel_layout = QVBoxLayout(middle_panel_widget)

        self.mode_key_details_group = QGroupBox("Mode Key Details")
        self.mode_key_details_layout = QFormLayout()
        self.mode_key_details_group.setLayout(self.mode_key_details_layout)
        middle_panel_layout.addWidget(self.mode_key_details_group)
        # Fields for ModeKey details:
        self.mk_key_name_edit = QLineEdit()
        self.mk_key_name_edit.editingFinished.connect(self.update_current_mk_name)
        self.mode_key_details_layout.addRow("Key Name (File):", self.mk_key_name_edit)
        self.mk_vis_job_combo = QComboBox()
        for job_id, desc in VIS_JOB_MAP.items():
            self.mk_vis_job_combo.addItem(f"{desc} (ID: {job_id})", userData=job_id)
        self.mk_vis_job_combo.currentIndexChanged.connect(
            self.update_current_mk_vis_job
        )
        self.mode_key_details_layout.addRow("Vis Job:", self.mk_vis_job_combo)
        self.mk_type_label = QLabel()  # Will display internal type
        self.mode_key_details_layout.addRow("Type (Internal):", self.mk_type_label)
        # Add more mk fields (unknowns) if needed later

        middle_panel_layout.addWidget(QLabel("<b>Variants</b>"))
        self.variants_list_widget = QListWidget()
        self.variants_list_widget.currentItemChanged.connect(self.on_variant_selected)
        middle_panel_layout.addWidget(self.variants_list_widget)
        variant_buttons_layout = QHBoxLayout()
        add_variant_button = QPushButton("Add Variant")
        add_variant_button.clicked.connect(self.add_variant_to_current_key)
        remove_variant_button = QPushButton("Remove Variant")
        remove_variant_button.clicked.connect(self.remove_selected_variant)
        variant_buttons_layout.addWidget(add_variant_button)
        variant_buttons_layout.addWidget(remove_variant_button)
        middle_panel_layout.addLayout(variant_buttons_layout)
        self.splitter.addWidget(middle_panel_widget)

        # Right Panel: AnimationSetVariant Details
        # This will hold an instance of AnimationSetVariantWidget
        self.variant_detail_scroll_area = QScrollArea()  # Variant details can be long
        self.variant_detail_scroll_area.setWidgetResizable(True)
        self.variant_detail_scroll_area.setMinimumWidth(
            300
        )  # Ensure it has some base width
        self.variant_details_widget_container = (
            QWidget()
        )  # Placeholder, real widget will be set
        self.variant_detail_scroll_area.setWidget(
            self.variant_details_widget_container
        )  # initial empty
        self.splitter.addWidget(self.variant_detail_scroll_area)
        self.active_variant_widget: AnimationSetVariantWidget | None = (
            None  # To hold the active editor
        )

        self.splitter.setSizes([200, 250, 350])  # Initial rough sizes

        self.connect_signals()
        self.clear_data()
        self.setEnabled(False)

    def connect_signals(self):
        self.version_spin.valueChanged.connect(self.update_anim_set_data_and_visibility)
        self.revision_spin.valueChanged.connect(
            self.update_anim_set_data_and_visibility
        )
        # ... other general property signals ...
        self.run_speed_spin.valueChanged.connect(
            lambda v: (
                setattr(self.animation_set_data, "default_run_speed", v)
                if self.animation_set_data
                else None
            )
        )
        self.walk_speed_spin.valueChanged.connect(
            lambda v: (
                setattr(self.animation_set_data, "default_walk_speed", v)
                if self.animation_set_data
                else None
            )
        )
        self.mode_change_type_spin.valueChanged.connect(
            lambda v: (
                setattr(self.animation_set_data, "mode_change_type", v)
                if self.animation_set_data
                else None
            )
        )
        self.hovering_ground_check.stateChanged.connect(
            lambda s: (
                setattr(
                    self.animation_set_data,
                    "hovering_ground",
                    1 if s == Qt.CheckState.Checked.value else 0,
                )
                if self.animation_set_data
                else None
            )
        )
        self.fly_bank_scale_spin.valueChanged.connect(
            lambda v: (
                setattr(self.animation_set_data, "fly_bank_scale", v)
                if self.animation_set_data
                else None
            )
        )
        self.fly_accel_scale_spin.valueChanged.connect(
            lambda v: (
                setattr(self.animation_set_data, "fly_accel_scale", v)
                if self.animation_set_data
                else None
            )
        )
        self.fly_hit_scale_spin.valueChanged.connect(
            lambda v: (
                setattr(self.animation_set_data, "fly_hit_scale", v)
                if self.animation_set_data
                else None
            )
        )
        self.align_to_terrain_check.stateChanged.connect(
            lambda s: (
                setattr(
                    self.animation_set_data,
                    "allign_to_terrain",
                    1 if s == Qt.CheckState.Checked.value else 0,
                )
                if self.animation_set_data
                else None
            )
        )

    def set_data(self, anim_set_data: AnimationSet | None):
        self.animation_set_data = anim_set_data
        if self.animation_set_data:
            # Block signals for general properties
            widgets_to_block = [
                self.version_spin,
                self.revision_spin,
                self.run_speed_spin,
                self.walk_speed_spin,
                self.mode_change_type_spin,
                self.hovering_ground_check,
                self.fly_bank_scale_spin,
                self.fly_accel_scale_spin,
                self.fly_hit_scale_spin,
                self.align_to_terrain_check,
            ]
            for widget in widgets_to_block:
                widget.blockSignals(True)

            self.version_spin.setValue(self.animation_set_data.version)
            self.revision_spin.setValue(self.animation_set_data.revision)
            self.run_speed_spin.setValue(self.animation_set_data.default_run_speed)
            self.walk_speed_spin.setValue(self.animation_set_data.default_walk_speed)
            self.mode_change_type_spin.setValue(
                self.animation_set_data.mode_change_type
            )
            self.hovering_ground_check.setChecked(
                bool(self.animation_set_data.hovering_ground)
            )
            self.fly_bank_scale_spin.setValue(self.animation_set_data.fly_bank_scale)
            self.fly_accel_scale_spin.setValue(self.animation_set_data.fly_accel_scale)
            self.fly_hit_scale_spin.setValue(self.animation_set_data.fly_hit_scale)
            self.align_to_terrain_check.setChecked(
                bool(self.animation_set_data.allign_to_terrain)
            )

            for widget in widgets_to_block:
                widget.blockSignals(False)

            self.update_conditional_visibility()
            self.populate_mode_keys_list()
            self.setEnabled(True)
        else:
            self.clear_data()
            self.setEnabled(False)

    def clear_data(self):
        self.animation_set_data = None
        self.current_mode_key = None
        self.current_variant = None

        # Clear general properties (similar to before)
        self.version_spin.setValue(self.version_spin.minimum())
        # ... clear other general property widgets ...
        self.update_conditional_visibility()

        self.mode_keys_list_widget.clear()
        self.clear_mode_key_details()
        self.variants_list_widget.clear()
        self.clear_variant_details()
        self.setEnabled(False)

    def update_anim_set_data_and_visibility(self):
        if not self.animation_set_data:
            return
        self.animation_set_data.version = self.version_spin.value()
        self.animation_set_data.revision = self.revision_spin.value()
        self.log_widget.log_message(
            f"AnimationSet version/revision updated. V: {self.animation_set_data.version}, R: {self.animation_set_data.revision}"
        )
        self.update_conditional_visibility()

    def update_conditional_visibility(self):
        # ... (logic remains the same as your provided version) ...
        version_ok = False
        revision_ok_lvl1 = False
        revision_ok_lvl2 = False
        revision_ok_lvl3 = False
        current_version = self.version_spin.value()
        current_revision = self.revision_spin.value()
        version_ok = current_version >= 6
        if version_ok:
            revision_ok_lvl1 = current_revision >= 2
            revision_ok_lvl2 = current_revision >= 5
            revision_ok_lvl3 = current_revision >= 6

        is_visible_lvl1 = version_ok and revision_ok_lvl1
        self.mode_change_type_spin.setVisible(is_visible_lvl1)
        self.conditional_props_layout.labelForField(
            self.mode_change_type_spin
        ).setVisible(is_visible_lvl1)
        self.hovering_ground_check.setVisible(is_visible_lvl1)

        is_visible_lvl2 = version_ok and revision_ok_lvl2
        self.fly_bank_scale_spin.setVisible(is_visible_lvl2)
        self.conditional_props_layout.labelForField(
            self.fly_bank_scale_spin
        ).setVisible(is_visible_lvl2)
        self.fly_accel_scale_spin.setVisible(is_visible_lvl2)
        self.conditional_props_layout.labelForField(
            self.fly_accel_scale_spin
        ).setVisible(is_visible_lvl2)
        self.fly_hit_scale_spin.setVisible(is_visible_lvl2)
        self.conditional_props_layout.labelForField(self.fly_hit_scale_spin).setVisible(
            is_visible_lvl2
        )

        is_visible_lvl3 = version_ok and revision_ok_lvl3
        self.align_to_terrain_check.setVisible(is_visible_lvl3)
        self.conditional_props_group.setVisible(
            is_visible_lvl1 or is_visible_lvl2 or is_visible_lvl3
        )

    def populate_mode_keys_list(self):
        self.mode_keys_list_widget.clear()
        self.clear_mode_key_details()  # Also clear details and variant list
        if self.animation_set_data and self.animation_set_data.mode_animation_keys:
            for i, mode_key in enumerate(self.animation_set_data.mode_animation_keys):
                display_text = f"{i+1}. {mode_key.file if mode_key.file else 'Untitled Key'} (VisJob: {VIS_JOB_MAP.get(mode_key.vis_job, str(mode_key.vis_job))})"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, mode_key)  # Store ref to object
                self.mode_keys_list_widget.addItem(item)
        if self.mode_keys_list_widget.count() > 0:
            self.mode_keys_list_widget.setCurrentRow(0)  # Select first item

    def on_mode_key_selected(
        self, current_item: QListWidgetItem, previous_item: QListWidgetItem
    ):
        if not current_item:
            self.clear_mode_key_details()
            return

        self.current_mode_key = current_item.data(Qt.ItemDataRole.UserRole)
        if self.current_mode_key:
            self.mk_key_name_edit.blockSignals(True)
            self.mk_vis_job_combo.blockSignals(True)

            self.mk_key_name_edit.setText(self.current_mode_key.file)
            self.mk_type_label.setText(str(self.current_mode_key.type))

            # Set VisJob ComboBox
            vis_job_id = self.current_mode_key.vis_job
            index = self.mk_vis_job_combo.findData(vis_job_id)
            if index != -1:
                self.mk_vis_job_combo.setCurrentIndex(index)
            else:  # Add temporary item for unknown ID
                self.mk_vis_job_combo.addItem(f"Unknown (ID: {vis_job_id})", vis_job_id)
                self.mk_vis_job_combo.setCurrentIndex(self.mk_vis_job_combo.count() - 1)

            self.mk_key_name_edit.blockSignals(False)
            self.mk_vis_job_combo.blockSignals(False)

            self.mode_key_details_group.setEnabled(True)
            self.populate_variants_list()
        else:
            self.clear_mode_key_details()

    def clear_mode_key_details(self):
        self.current_mode_key = None
        self.mk_key_name_edit.clear()
        self.mk_type_label.clear()
        self.mk_vis_job_combo.setCurrentIndex(-1)
        self.mode_key_details_group.setEnabled(False)
        self.variants_list_widget.clear()
        self.clear_variant_details()

    def update_current_mk_name(self):
        if self.current_mode_key:
            new_name = self.mk_key_name_edit.text()
            if self.current_mode_key.file != new_name:
                self.current_mode_key.file = new_name
                self.current_mode_key.length = len(new_name.encode("utf-8"))
                self.log_widget.log_message(
                    f"ModeKey '{self.current_mode_key.file}' name updated."
                )
                # Update QListWidget item text
                current_row = self.mode_keys_list_widget.currentRow()
                if current_row >= 0:
                    item = self.mode_keys_list_widget.item(current_row)
                    display_text = f"{current_row+1}. {new_name} (VisJob: {VIS_JOB_MAP.get(self.current_mode_key.vis_job, str(self.current_mode_key.vis_job))})"
                    item.setText(display_text)

    def update_current_mk_vis_job(self, index):
        if self.current_mode_key and index >= 0:
            selected_job_id = self.mk_vis_job_combo.itemData(index)
            if self.current_mode_key.vis_job != selected_job_id:
                self.current_mode_key.vis_job = selected_job_id
                self.log_widget.log_message(
                    f"ModeKey '{self.current_mode_key.file}' VisJob set to ID: {selected_job_id}"
                )
                # Update QListWidget item text
                current_row = self.mode_keys_list_widget.currentRow()
                if current_row >= 0:
                    item = self.mode_keys_list_widget.item(current_row)
                    display_text = f"{current_row+1}. {self.current_mode_key.file} (VisJob: {VIS_JOB_MAP.get(selected_job_id, str(selected_job_id))})"
                    item.setText(display_text)

    def populate_variants_list(self):
        self.variants_list_widget.clear()
        self.clear_variant_details()
        if self.current_mode_key and self.current_mode_key.animation_set_variants:
            for i, variant in enumerate(self.current_mode_key.animation_set_variants):
                item = QListWidgetItem(
                    f"{i+1}. {variant.file if variant.file else 'Untitled Variant'}"
                )
                item.setData(Qt.ItemDataRole.UserRole, variant)
                self.variants_list_widget.addItem(item)
        if self.variants_list_widget.count() > 0:
            self.variants_list_widget.setCurrentRow(0)

    def on_variant_selected(
        self, current_item: QListWidgetItem, previous_item: QListWidgetItem
    ):
        if not current_item:
            self.clear_variant_details()
            return

        self.current_variant = current_item.data(Qt.ItemDataRole.UserRole)
        if self.current_variant:
            if not self.active_variant_widget:  # Create if it doesn't exist
                self.active_variant_widget = AnimationSetVariantWidget(
                    self.current_variant, self.drs_handler, self.log_widget
                )
                self.variant_detail_scroll_area.setWidget(self.active_variant_widget)
            else:  # Reuse and update
                self.active_variant_widget.update_variant_data(self.current_variant)
            self.active_variant_widget.setVisible(True)
        else:
            self.clear_variant_details()

    def clear_variant_details(self):
        self.current_variant = None
        if self.active_variant_widget:
            self.active_variant_widget.setVisible(False)  # Hide it
            # Or to truly clear, you might reset its fields:
            # self.active_variant_widget.update_variant_data(AnimationSetVariant()) # Pass a dummy empty variant

    def add_mode_animation_key(self):
        if not self.animation_set_data:
            self.log_widget.log_message(
                "Cannot add ModeAnimationKey: AnimationSet data not loaded."
            )
            return

        new_key = ModeAnimationKey()
        new_key.file = f"NewKey_{len(self.animation_set_data.mode_animation_keys) + 1}"
        new_key.length = len(new_key.file.encode("utf-8"))
        if self.animation_set_data.version == 2:
            new_key.type = 2
        else:
            new_key.type = 6  # Common default

        self.animation_set_data.mode_animation_keys.append(new_key)
        self.animation_set_data.mode_animation_key_count = len(
            self.animation_set_data.mode_animation_keys
        )
        self.log_widget.log_message(f"Added new Mode Animation Key: {new_key.file}")
        self.populate_mode_keys_list()
        self.mode_keys_list_widget.setCurrentRow(self.mode_keys_list_widget.count() - 1)

    def remove_mode_animation_key(self):
        if not self.current_mode_key or not self.animation_set_data:
            self.log_widget.log_message(
                "No ModeKey selected to remove or data not loaded."
            )
            return
        current_row = self.mode_keys_list_widget.currentRow()
        if current_row < 0:
            return

        key_to_remove = self.mode_keys_list_widget.item(current_row).data(
            Qt.ItemDataRole.UserRole
        )
        if key_to_remove in self.animation_set_data.mode_animation_keys:
            self.animation_set_data.mode_animation_keys.remove(key_to_remove)
            self.animation_set_data.mode_animation_key_count = len(
                self.animation_set_data.mode_animation_keys
            )
            self.log_widget.log_message(f"Removed ModeKey: {key_to_remove.file}")
            self.populate_mode_keys_list()  # Repopulate and auto-select first or none
            # If list becomes empty, details should clear. Otherwise, first item selected by populate_mode_keys_list
            if self.mode_keys_list_widget.count() == 0:
                self.clear_mode_key_details()

    def add_variant_to_current_key(self):
        if not self.current_mode_key:
            self.log_widget.log_message("No ModeKey selected to add a variant to.")
            return
        new_variant = AnimationSetVariant()
        new_variant.file = (
            f"new_ska_{len(self.current_mode_key.animation_set_variants) + 1}"
        )
        new_variant.length = len(new_variant.file.encode("utf-8"))
        # Default version for new variant
        if self.current_mode_key.type == 6:
            new_variant.version = 7
        elif self.current_mode_key.type <= 5:
            new_variant.version = 5
        else:
            new_variant.version = (
                self.animation_set_data.version if self.animation_set_data else 7
            )

        self.current_mode_key.animation_set_variants.append(new_variant)
        self.current_mode_key.variant_count = len(
            self.current_mode_key.animation_set_variants
        )
        self.log_widget.log_message(
            f"Added new variant to key '{self.current_mode_key.file}'"
        )
        self.populate_variants_list()
        self.variants_list_widget.setCurrentRow(self.variants_list_widget.count() - 1)

    def remove_selected_variant(self):
        if not self.current_variant or not self.current_mode_key:
            self.log_widget.log_message(
                "No Variant selected to remove or ModeKey not selected."
            )
            return
        current_row = self.variants_list_widget.currentRow()
        if current_row < 0:
            return

        variant_to_remove = self.variants_list_widget.item(current_row).data(
            Qt.ItemDataRole.UserRole
        )
        if variant_to_remove in self.current_mode_key.animation_set_variants:
            self.current_mode_key.animation_set_variants.remove(variant_to_remove)
            self.current_mode_key.variant_count = len(
                self.current_mode_key.animation_set_variants
            )
            self.log_widget.log_message(
                f"Removed variant '{variant_to_remove.file}' from key '{self.current_mode_key.file}'"
            )
            self.populate_variants_list()  # Repopulate and auto-select first or none
            if self.variants_list_widget.count() == 0:
                self.clear_variant_details()

    def commit_changes(self):
        if self.animation_set_data:
            self.log_widget.log_message(
                "AnimationSet changes committed to internal data object."
            )
            # Data should be up-to-date via signals or direct modification.
            # Ensure counts are correct if lists were manipulated directly elsewhere
            self.animation_set_data.mode_animation_key_count = len(
                self.animation_set_data.mode_animation_keys
            )
            for mk in self.animation_set_data.mode_animation_keys:
                mk.variant_count = len(mk.animation_set_variants)

            if self.drs_handler.drs_object and hasattr(
                self.drs_handler.drs_object, "animation_set"
            ):
                self.drs_handler.update_node_size(
                    self.drs_handler.drs_object.animation_set
                )
