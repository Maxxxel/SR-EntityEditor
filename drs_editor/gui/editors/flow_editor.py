# drs_editor/gui/editors/flow_editor.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QFormLayout,
    QGroupBox,
)
from drs_editor.data_structures.drs_definitions import Flow, Vector4  #
from drs_editor.file_handlers.drs_handler import DRSHandler
from drs_editor.gui.log_widget import LogWidget


class FlowEditorWidget(QGroupBox):
    def __init__(
        self,
        flow_obj: Flow,
        drs_handler: DRSHandler,
        log_widget: LogWidget,
        parent=None,
    ):
        super().__init__("Flow Parameters", parent)
        self.flow_obj = flow_obj
        self.drs_handler = drs_handler
        self.log_widget = log_widget

        self.layout = QFormLayout(self)

        if self.flow_obj and self.flow_obj.length == 4:  #
            self._add_vector4_editor("Max Flow Speed", self.flow_obj.max_flow_speed)  #
            self._add_vector4_editor("Min Flow Speed", self.flow_obj.min_flow_speed)  #
            self._add_vector4_editor(
                "Flow Speed Change", self.flow_obj.flow_speed_change
            )  #
            self._add_vector4_editor("Flow Scale", self.flow_obj.flow_scale)  #
        else:
            self.layout.addRow(
                QLabel("Flow parameters not applicable or not loaded (length != 4).")
            )

    def _add_vector4_editor(self, label: str, vector4: Vector4):  #
        # Vector4 in drs_definitions has x,y,z,w and also an xyz Vector field.
        # We edit x,y,z,w.
        x_edit = QLineEdit(str(vector4.x))  #
        y_edit = QLineEdit(str(vector4.y))  #
        z_edit = QLineEdit(str(vector4.z))  #
        w_edit = QLineEdit(str(vector4.w))  #

        for comp_edit, comp_name in [
            (x_edit, "x"),
            (y_edit, "y"),
            (z_edit, "z"),
            (w_edit, "w"),
        ]:
            comp_edit.editingFinished.connect(
                lambda v=vector4, edit=comp_edit, name=comp_name, l=label: self.update_vector4_comp(
                    v, name, edit.text(), l
                )
            )
            self.layout.addRow(f"{label} ({comp_name.upper()}):", comp_edit)

    def update_vector4_comp(
        self, vector4: Vector4, component_name: str, value_str: str, vec_label: str
    ):
        try:
            new_val = float(value_str)
            old_val = getattr(vector4, component_name)
            if old_val != new_val:
                setattr(vector4, component_name, new_val)
                # Also update the .xyz Vector if component is x,y or z
                if component_name in ["x", "y", "z"] and hasattr(vector4, "xyz"):
                    if component_name == "x":
                        vector4.xyz.values[0] = new_val
                    elif component_name == "y":
                        vector4.xyz.values[1] = new_val
                    elif component_name == "z":
                        vector4.xyz.values[2] = new_val

                self.log_widget.log_message(
                    f"Flow '{vec_label}' component '{component_name}' changed: {old_val} -> {new_val}"
                )
                # self.drs_handler.update_node_size(self.parent_mesh_object) # Propagate if needed
        except ValueError:
            self.log_widget.log_message(
                f"Invalid float value for Flow '{vec_label}' component '{component_name}': {value_str}"
            )
            # Revert QLineEdit text to old value
            # edit_widget.setText(str(getattr(vector4, component_name)))
