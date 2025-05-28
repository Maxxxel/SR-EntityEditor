# drs_editor/gui/mesh_editor_tab.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QGroupBox,
    QFormLayout,
    QTabWidget,
    QSizePolicy,
)

# Make sure all editor widgets are imported
from drs_editor.data_structures.drs_definitions import BattleforgeMesh  #
from drs_editor.file_handlers.drs_handler import DRSHandler
from .log_widget import LogWidget
from .editors.texture_editor import TextureEditorWidget
from .editors.material_editor import MaterialEditorWidget
from .editors.flow_editor import FlowEditorWidget
from .editors.refraction_editor import RefractionEditorWidget


class MeshEditorTab(QWidget):
    def __init__(
        self,
        battleforge_mesh: BattleforgeMesh,
        drs_handler: DRSHandler,
        log_widget: LogWidget,
        parent=None,
    ):
        super().__init__(parent)
        self.battleforge_mesh = battleforge_mesh  #
        self.drs_handler = drs_handler
        self.log_widget = log_widget

        # Main layout for this MeshEditorTab widget
        self.top_level_layout = QVBoxLayout(self)
        self.top_level_layout.setContentsMargins(5, 5, 5, 5)  # Add some margin

        # 1. Mesh Information Section (stays at the top, not in a tab)
        self._create_info_section()  # This will add the info_group to self.top_level_layout

        # 2. Tab Widget for detailed editors
        self.editors_tab_widget = QTabWidget()
        self.top_level_layout.addWidget(self.editors_tab_widget)

        # Create and add editor tabs
        self._create_texture_tab()
        self._create_material_tab()
        self._create_flow_tab()
        self._create_refraction_tab()

    def _create_info_section(self):
        info_group = QGroupBox("Mesh Information")
        info_layout = QFormLayout()

        info_layout.addRow(
            "Vertex Count:", QLabel(str(self.battleforge_mesh.vertex_count))
        )  #
        info_layout.addRow(
            "Face Count:", QLabel(str(self.battleforge_mesh.face_count))
        )  #
        info_layout.addRow(
            "Mesh Data Count:", QLabel(str(self.battleforge_mesh.mesh_count))
        )  #
        # Add more basic info if desired

        info_group.setLayout(info_layout)
        self.top_level_layout.addWidget(
            info_group
        )  # Add info group to the main vertical layout

    def _create_texture_tab(self):
        # This QWidget will be the actual page for the tab.
        # It will contain the scroll area.
        texture_tab_page_widget = QWidget()
        texture_tab_page_layout = QVBoxLayout(texture_tab_page_widget)
        texture_tab_page_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Optional: remove margins if scroll area handles it
        texture_tab_page_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )  # Expand vertically
        texture_tab_page_layout.addWidget(
            scroll_area
        )  # Add scroll area to the tab page's layout

        # The TextureEditorWidget (QGroupBox) will be the content of the scroll area
        if hasattr(self.battleforge_mesh, "textures"):
            texture_editor_content_widget = (
                TextureEditorWidget(  # This is your QGroupBox
                    self.battleforge_mesh.textures,
                    self.drs_handler,
                    self.log_widget,
                    self.battleforge_mesh,
                )
            )
            scroll_area.setWidget(
                texture_editor_content_widget
            )  # Set group box as scrollable widget
            self.editors_tab_widget.addTab(
                texture_tab_page_widget, "Textures"
            )  # Add the page widget to the tab
        else:
            no_textures_label = QLabel(
                "Texture data (Textures object) not available in BattleforgeMesh."
            )
            # If there are no textures, you might not need a scroll area
            self.editors_tab_widget.addTab(no_textures_label, "Textures")

    def _create_material_tab(self):
        # Check if bool_parameter is applicable for the current mesh's material_parameters
        # From drs_definitions.py, BattleforgeMesh.read() shows bool_parameter is read for:
        # -86061050, -86061051, -86061052, -86061053, -86061054, -86061055
        applicable_params_for_bool_param = [
            -86061050,
            -86061051,
            -86061052,
            -86061053,
            -86061054,
            -86061055,
        ]

        if (
            self.battleforge_mesh.material_parameters
            in applicable_params_for_bool_param
        ):  #
            # Ensure bool_parameter attribute exists; it should if material_parameters is one of the above
            if hasattr(self.battleforge_mesh, "bool_parameter"):  #
                material_flags_editor_widget = (
                    MaterialEditorWidget(  # This is the new editor
                        self.battleforge_mesh, self.drs_handler, self.log_widget
                    )
                )
                self.editors_tab_widget.addTab(
                    material_flags_editor_widget, "Material Flags"
                )  # Updated tab name
            else:
                # This case should ideally not be reached if BattleforgeMesh.read is consistent
                self.editors_tab_widget.addTab(
                    QLabel(
                        "bool_parameter attribute missing despite applicable material_parameters."
                    ),
                    "Material Flags",
                )
        else:
            self.editors_tab_widget.addTab(
                QLabel(
                    "Material Flags (bool_parameter) not applicable for this mesh's material_parameters value."
                ),
                "Material Flags",
            )

    def _create_flow_tab(self):
        # Check if flow should be displayed based on material_parameters
        if self.battleforge_mesh.material_parameters == -86061050:  #
            if (
                hasattr(self.battleforge_mesh, "flow")
                and self.battleforge_mesh.flow.length == 4
            ):  #
                flow_editor_widget = FlowEditorWidget(
                    self.battleforge_mesh.flow, self.drs_handler, self.log_widget
                )  #
                self.editors_tab_widget.addTab(flow_editor_widget, "Flow")
            else:
                self.editors_tab_widget.addTab(
                    QLabel("Flow parameters applicable but data seems inconsistent."),
                    "Flow",
                )
        else:
            self.editors_tab_widget.addTab(
                QLabel("Flow parameters not applicable for this mesh's material type."),
                "Flow",
            )

    def _create_refraction_tab(self):
        applicable_params_for_refraction = [
            -86061050,
            -86061051,
            -86061053,
            -86061054,
            -86061055,
        ]  #
        if (
            self.battleforge_mesh.material_parameters
            in applicable_params_for_refraction
        ):  #
            if hasattr(self.battleforge_mesh, "refraction"):  #
                refraction_editor_widget = RefractionEditorWidget(
                    self.battleforge_mesh.refraction, self.drs_handler, self.log_widget
                )  #
                self.editors_tab_widget.addTab(refraction_editor_widget, "Refraction")
            else:
                self.editors_tab_widget.addTab(
                    QLabel("Refraction data structure missing."), "Refraction"
                )
        else:
            self.editors_tab_widget.addTab(
                QLabel(
                    "Refraction settings not applicable for this mesh's material type."
                ),
                "Refraction",
            )

    def commit_changes(self):
        """
        This method could be called to ensure all data from editor widgets
        is written back to the self.battleforge_mesh object if direct binding isn't used,
        though with direct signal/slot connections, this might be less necessary
        for individual field changes. It's still good for a global "apply".
        It should also call self.drs_handler.update_node_size(self.battleforge_mesh).
        """
        # Potentially iterate through tabs and call a "commit_changes_to_object" on each editor widget if they have one.
        # For now, individual editors are connected to update the model directly.
        self.log_widget.log_message(
            f"Changes for Mesh (Vertex Count: {self.battleforge_mesh.vertex_count}) reviewed/committed to internal DRS object."
        )  #
        self.drs_handler.update_node_size(self.battleforge_mesh)
