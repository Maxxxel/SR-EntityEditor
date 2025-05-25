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
)  # Added QComboBox
from PyQt6.QtCore import Qt
from drs_editor.data_structures.drs_definitions import (
    AnimationSet,
    ModeAnimationKey,
    AnimationSetVariant,
)
from drs_editor.file_handlers.drs_handler import DRSHandler
from drs_editor.gui.log_widget import LogWidget

# from .ska_editor_dialog import SkaEditorDialog # Placeholder

# --- VIS JOB MAP ---
VIS_JOB_MAP = {
    0: "Idle",
    1: "Walk",
    2: "Run",
    3: "Spawn",
    4: "HitFromBack",
    5: "Cheer / Emote",
    6: "SpellTargetShotSequenceAreaShotDelay / SpellTargetShotSequenceAreaIdle",
    7: "UnDeploy",
    8: "Attack",
    9: "Deploy / Charge Attack Run",
    10: "WormMovement Start",
    11: "HitFromFront",
    12: "Die",
    13: "CorpseRot",
    14: "SpellTargetShotSequenceAreaRecoil / HitFromLeft",
    15: "Special Melee Attack (AnimTagID 114)",
    16: "Special Melee Attack (AnimTagID 115)",
    17: "WormMovement Loop",
    18: "Cast",
    19: "CastResolve",
    21: "CastResolveAir",
    22: "CastAir",
    23: "HitFromRight",
    24: "Talk",
    27: "Impactful Movement / Trample",
    28: "WormMovement End",
    29: "PushBackStandUp Start",
    30: "PushBackStandUp Loop",
    31: "PushBackStandUp End",
    35: "Immobilized / Trapped",
    99: "Trailer",
    128: "StampedeStart",
    129: "StampedeRun",
    130: "StampedeStop",
    131: "EraseOverTimeInit / EraseOverTimeStart",
    132: "EraseOverTimeWork / EraseOverTimeLoop",
    133: "EraseOverTimeShutDown / EraseOverTimeEnd",
    134: "GroundPounder (Tremor) Cast",
    135: "GroundPounder (Tremor) Resolve",
    136: "Firelance (Emberstrike) Cast",
    137: "Firelance (Emberstrike) Resolve",
    138: "Paralyze Cast",
    139: "Paralyze Resolve",
    140: "ThrowFlames Init",
    141: "ThrowFlames Work",
    142: "ThrowFlames ShutDown",
    143: "ThrowShadowFlames Init",
    144: "ThrowShadowFlames Work",
    145: "ThrowShadowFlames ShutDown",
    146: "Conflagration Init",
    147: "Conflagration Work",
    148: "Conflagration ShutDown",
    149: "Exhaust Cast",
    150: "Exhaust Resolve",
    151: "UnholyArmor Cast",
    152: "UnholyArmor Resolve",
    153: "Frenzy Cast",
    154: "Frenzy Resolve",
    155: "SummonSkeletons Cast",
    156: "SummonSkeletons Resolve",
    157: "Deathwish Cast",
    158: "Deathwish Resolve",
    159: "SacrificeSquad Cast",
    160: "SacrificeSquad Resolve",
    161: "SuicidalBomb Cast",
    162: "SuicidalBomb Resolve",
    163: "CrushWalls Cast",
    164: "CrushWalls Resolve",
    165: "Rage (AnimTagID 31)",
    166: "Rage (AnimTagID 32)",
    167: "DisableTower Cast",
    168: "DisableTower Resolve",
    169: "PowerSteal Cast",
    170: "PowerSteal Resolve",
    173: "Heal Cast",
    174: "Heal Resolve",
    175: "ThunderousRoar Cast",
    176: "ThunderousRoar Resolve",
    177: "Heal Channel Start",
    178: "Heal Channel Loop",
    179: "Heal Channel End",
    180: "Paralyze Channel Start",
    181: "Paralyze Channel Loop",
    182: "Paralyze Channel End",
    183: "DisableTower CastAir",
    184: "DisableTower ResolveAir",
    185: "PreparedSalvo Cast",
    186: "PreparedSalvo Resolve",
    187: "PreparedSalvo CastAir",
    188: "PreparedSalvo ResolveAir",
    189: "Special Burrow Cast",
    190: "Special Burrow Resolve",
    191: "Turret Fire To Front Cast",
    192: "Turret Fire To Front Resolve",
    193: "Turret Fire To Left Cast",
    194: "Turret Fire To Left Resolve",
    195: "Turret Fire To Back Cast",
    196: "Turret Fire To Back Resolve",
    197: "Turret Fire To Right Cast",
    198: "Turret Fire To Right Resolve",
    199: "Charge Attack",
    200: "SummonDemon Cast",
    201: "SummonDemon Resolve",
    202: "AreaFreeze Cast",
    203: "AreaFreeze Resolve",
    204: "HealingRay Cast",
    205: "HealingRay Resolve",
    206: "IceShield Channel Start (Previously Winter Witch aura)",
    207: "IceShield Channel Loop",
    208: "IceShield Channel End",
    209: "FrostBeam Start",
    210: "FrostBeam Loop",
    211: "FrostBeam End",
    212: "AntimagicField Start",
    213: "AntimagicField Loop",
    214: "AntimagicField End",
    215: "FireStream Start",
    216: "FireStream Loop",
    217: "FireStream End",
    218: "StasisField Cast",
    219: "StasisField Resolve",
    220: "BurningLiquid Cast",
    221: "BurningLiquid Resolve",
    222: "MindControl Cast",
    223: "MindControl Resolve",
    224: "IceShield Target Cast",
    225: "IceShield Target Resolve",
    226: "SonicScream Cast",
    227: "SonicScream Resolve",
    228: "TeleportSelf Cast",
    229: "TeleportSelf Resolve",
    230: "Repair Channel Start (AnimTagID 110)",
    231: "Repair Channel Loop (AnimTagID 110)",
    232: "Repair Channel End (AnimTagID 110)",
    233: "Strike Cast",
    234: "Strike Resolve",
    235: "CriticalMass Cast",
    236: "CriticalMass Resolve",
    237: "SiegeTrumpet Cast",
    238: "SiegeTrumpet Resolve",
    239: "Bracing Zone Cast",
    240: "Bracing Zone Resolve",
    241: "Fireball Cast",
    242: "Fireball Resolve",
    243: "MassSleep Cast",
    244: "MassSleep Resolve",
    245: "ChainInsectRay Cast",
    246: "ChainInsectRay Resolve",
    247: "Repair Channel Start (AnimTagID 121)",
    248: "Repair Channel Loop (AnimTagID 121)",
    249: "Repair Channel End (AnimTagID 121)",
    250: "BombRaid Cast",
    251: "BombRaid Resolve",
    252: "LifeLink Start",
    253: "LifeLink Loop",
    254: "LifeLink End",
    255: "WormMovement_Hack Cast",
    256: "WormMovement_Hack Resolve",
    257: "skel_giant_hammer_attack_pve1 Cast",
    258: "skel_giant_hammer_attack_pve1 Resolve",
    259: "IceBombardment Near Start",
    260: "IceBombardment Near Loop",
    261: "IceBombardment Near End",
    262: "IceBombardment Far Start",
    263: "IceBombardment Far Loop",
    264: "IceBombardment Far End",
    265: "ParalyzingRoar Cast",
    266: "ParalyzingRoar Resolve",
    267: "SacrificeKill Cast",
    268: "SacrificeKill Resolve",
    269: "LifeTransfer Cast",
    270: "LifeTransfer Resolve",
    271: "Earthquake Start",
    272: "Earthquake Loop",
    273: "Earthquake End",
    274: "PVEChannel Start",
    275: "PVEChannel Loop",
    276: "PVEChannel End",
    277: "PVECastResolve Cast",
    278: "PVECastResolve Resolve",
    279: "PVEMelee Attack",
    280: "AttachToBuilding Start",
    281: "AttachToBuilding Loop",
    282: "AttachToBuilding End",
    283: "RepairCast Cast",
    284: "RepairCast Resolve",
    285: "RageCastStage1 Cast",
    286: "RageCastStage1 Resolve",
    287: "RageCastStage1 CastAir",
    288: "RageCastStage1 ResolveAir",
    289: "RageCastStage2 Cast",
    290: "RageCastStage2 Resolve",
    291: "RageCastStage2 CastAir",
    292: "RageCastStage2 ResolveAir",
    293: "SuicideAttack Cast",
    294: "SuicideAttack Resolve",
    295: "RelocateBuilding Cast",
    296: "RelocateBuilding Resolve",
    297: "DeathCounter Cast",
    298: "DeathCounter Resolve",
    299: "TombOfDeath Start",
    300: "TombOfDeath Loop",
    301: "TombOfDeath End",
    302: "VersatileAirSpecial Cast",
    303: "VersatileAirSpecial Resolve",
    304: "PVECastResolve2 Cast",
    305: "PVECastResolve2 Resolve",
    306: "Taunt Cast",
    307: "Taunt Resolve",
    308: "Swap Cast",
    309: "Swap Resolve",
    310: "Disenchant Cast",
    311: "Disenchant Resolve",
    312: "GravitySurge Cast",
    313: "GravitySurge Resolve",
    314: "Enrage Cast",
    315: "Enrage Resolve",
    316: "SpecialRangedAir Cast",
    317: "SpecialRangedAir Resolve",
    318: "GlobalBuffChannel Start",
    319: "GlobalBuffChannel Loop",
    320: "GlobalBuffChannel End",
    321: "Harpoon Cast",
    322: "Harpoon Resolve",
    323: "ThrowMines Cast",
    324: "ThrowMines Resolve",
}
# --- End VIS JOB MAP ---


class AnimationSetVariantWidget(QGroupBox):
    # ... (This class remains the same as your last provided version) ...
    def __init__(
        self,
        variant: AnimationSetVariant,
        anim_set: AnimationSet,
        drs_handler: DRSHandler,
        log_widget: LogWidget,
        parent=None,
    ):
        super().__init__(
            f"Variant: {variant.file if variant.file else 'New Variant'}", parent
        )  # Handle empty file name
        self.variant = variant
        self.anim_set = anim_set
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
        self.start_spin.setRange(0.0, 1000.0)
        self.start_spin.setDecimals(3)
        self.start_spin.setValue(self.variant.start)
        self.start_spin.valueChanged.connect(self.update_start)
        self.layout.addRow("Start:", self.start_spin)

        self.end_spin = QDoubleSpinBox()
        self.end_spin.setRange(0.0, 1000.0)
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

    def update_field_visibility(self):
        version = self.variant.version
        form_layout = self.layout

        self.start_spin.setVisible(version >= 4)
        start_label = form_layout.labelForField(self.start_spin)
        if start_label:
            start_label.setVisible(version >= 4)

        self.end_spin.setVisible(version >= 4)
        end_label = form_layout.labelForField(self.end_spin)
        if end_label:
            end_label.setVisible(version >= 4)

        self.allows_ik_check.setVisible(version >= 5)
        allows_ik_label = form_layout.labelForField(self.allows_ik_check)
        if allows_ik_label:
            allows_ik_label.setVisible(version >= 5)

        self.force_no_blend_check.setVisible(version >= 7)
        force_no_blend_label = form_layout.labelForField(self.force_no_blend_check)
        if force_no_blend_label:
            force_no_blend_label.setVisible(version >= 7)

    def update_ska_file(self):
        new_file = self.ska_file_edit.text()
        if self.variant.file != new_file:
            self.variant.file = new_file
            self.variant.length = len(new_file.encode("utf-8"))
            self.setTitle(f"Variant: {new_file if new_file else 'Untitled'}")
            self.log_widget.log_message(f"Variant SKA file changed to: {new_file}")

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
        self.log_widget.log_message(
            f"Attempting to open SKA editor for: {self.variant.file} (Not Yet Implemented)"
        )
        # ... (rest of placeholder SKA path logic from previous response) ...
        ska_file_path = ""
        if self.drs_handler.filepath and self.variant.file:
            base_dir = os.path.dirname(self.drs_handler.filepath)
            potential_path = os.path.join(base_dir, self.variant.file + ".ska")
            if not os.path.exists(potential_path) and not os.path.isabs(
                self.variant.file
            ):
                common_subdirs = [
                    "../anim",
                    "../animations",
                    "../ska",
                    "anim",
                    "animations",
                    "ska",
                ]
                for subdir in common_subdirs:
                    test_path = os.path.join(
                        base_dir, subdir, self.variant.file + ".ska"
                    )
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
                    f"Could not find SKA file: {self.variant.file}.ska\nSearched near: {potential_path}",
                )
        else:
            QMessageBox.warning(
                self, "SKA File", "SKA filename or DRS path is not set."
            )


class ModeAnimationKeyWidget(QGroupBox):
    def __init__(
        self,
        mode_key: ModeAnimationKey,
        anim_set: AnimationSet,
        drs_handler: DRSHandler,
        log_widget: LogWidget,
        parent=None,
    ):
        super().__init__(
            f"Key: {mode_key.file if mode_key.file else 'New Key'}", parent
        )  # Handle empty file name
        self.mode_key = mode_key
        self.anim_set = anim_set
        self.drs_handler = drs_handler
        self.log_widget = log_widget

        self.main_layout = QVBoxLayout(self)
        self.details_layout = QFormLayout()
        self.main_layout.addLayout(self.details_layout)

        # --- Vis Job ComboBox ---
        self.vis_job_combo = QComboBox()
        self.vis_job_combo.setToolTip("Select the visual job/animation type.")
        # Populate ComboBox
        for job_id, description in VIS_JOB_MAP.items():
            self.vis_job_combo.addItem(f"{description} (ID: {job_id})", userData=job_id)

        # Set current value
        current_vis_job_id = self.mode_key.vis_job
        index = self.vis_job_combo.findData(current_vis_job_id)
        if index != -1:
            self.vis_job_combo.setCurrentIndex(index)
        else:
            # If ID not in map, add it as a temporary item or show raw ID
            self.vis_job_combo.addItem(
                f"Unknown Vis Job (ID: {current_vis_job_id})",
                userData=current_vis_job_id,
            )
            self.vis_job_combo.setCurrentIndex(self.vis_job_combo.count() - 1)
            self.log_widget.log_message(
                f"Warning: Vis Job ID {current_vis_job_id} not found in predefined map for key '{self.mode_key.file}'."
            )

        self.vis_job_combo.currentIndexChanged.connect(self.update_vis_job)
        self.details_layout.addRow("Vis Job:", self.vis_job_combo)
        # --- End Vis Job ComboBox ---

        self.type_label = QLabel(str(self.mode_key.type))  # Display type
        self.details_layout.addRow("Type (Internal):", self.type_label)

        self.key_name_edit = QLineEdit(self.mode_key.file)  # Allow editing key name
        self.key_name_edit.editingFinished.connect(self.update_key_name)
        self.details_layout.addRow("Key Name (File):", self.key_name_edit)

        # Placeholder for other ModeAnimationKey fields (unknowns)
        # Example: self.unknown1_spin = QSpinBox(); self.details_layout.addRow("Unknown1:", self.unknown1_spin) ...

        self.variants_container = QWidget()
        self.variants_layout = QVBoxLayout(self.variants_container)
        self.variants_layout.setContentsMargins(0, 5, 0, 0)
        self.variants_layout.setSpacing(3)

        variants_group_label = QLabel("<b>Variants:</b>")  # Make label bold
        self.main_layout.addWidget(variants_group_label)
        self.main_layout.addWidget(self.variants_container)

        self.refresh_variants_ui()

        add_variant_button = QPushButton("Add Variant to this Key")
        add_variant_button.clicked.connect(self.add_variant)
        self.main_layout.addWidget(add_variant_button)

    def update_key_name(self):
        new_name = self.key_name_edit.text()
        if self.mode_key.file != new_name:
            self.mode_key.file = new_name
            self.mode_key.length = len(new_name.encode("utf-8"))
            self.setTitle(
                f"Key: {new_name if new_name else 'Untitled'}"
            )  # Update GroupBox title
            self.log_widget.log_message(f"ModeAnimationKey name changed to: {new_name}")

    def update_vis_job(self, index):
        selected_job_id = self.vis_job_combo.itemData(index)
        if selected_job_id is not None and self.mode_key.vis_job != selected_job_id:
            self.mode_key.vis_job = selected_job_id
            self.log_widget.log_message(
                f"Vis Job for key '{self.mode_key.file}' set to ID: {selected_job_id} ({self.vis_job_combo.currentText()})"
            )

    def refresh_variants_ui(self):
        while self.variants_layout.count():
            child = self.variants_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for variant in self.mode_key.animation_set_variants:
            var_widget = AnimationSetVariantWidget(
                variant, self.anim_set, self.drs_handler, self.log_widget
            )
            self.variants_layout.addWidget(var_widget)

    def add_variant(self):
        new_variant = AnimationSetVariant()
        new_variant.file = f"new_ska_{len(self.mode_key.animation_set_variants) + 1}"
        new_variant.length = len(new_variant.file.encode("utf-8"))
        # You might want to default variant.version based on parent ModeAnimationKey.type or AnimationSet.version
        # For example, variant.version = 7 (common default)
        if (
            self.mode_key.type == 6
        ):  # Default for type 6 ModeKey often has variant version 7
            new_variant.version = 7
        elif self.mode_key.type <= 5:  # Older types might have older variant versions
            new_variant.version = 5  # Example
        else:
            new_variant.version = self.anim_set.version  # Fallback or another logic

        self.mode_key.animation_set_variants.append(new_variant)
        self.mode_key.variant_count = len(self.mode_key.animation_set_variants)
        self.log_widget.log_message(f"Added new variant to key '{self.mode_key.file}'")
        self.refresh_variants_ui()


# ... (AnimationSetEditorWidget class remains, with changes shown below) ...
class AnimationSetEditorWidget(QWidget):
    def __init__(self, drs_handler: DRSHandler, log_widget: LogWidget, parent=None):
        super().__init__(parent)
        self.drs_handler = drs_handler
        self.log_widget = log_widget
        self.animation_set_data: AnimationSet | None = None

        self.main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(scroll_area)

        self.content_widget = QWidget()
        scroll_area.setWidget(self.content_widget)
        self.content_layout = QVBoxLayout(self.content_widget)

        general_props_group = QGroupBox("General Properties")
        self.general_props_layout = QFormLayout()
        general_props_group.setLayout(self.general_props_layout)
        self.content_layout.addWidget(general_props_group)

        self.version_spin = QSpinBox()
        self.version_spin.setRange(2, 7)  # Common range for AnimationSet version
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

        self.conditional_props_group = QGroupBox("Conditional Properties")
        self.conditional_props_layout = QFormLayout()
        self.conditional_props_group.setLayout(self.conditional_props_layout)
        self.content_layout.addWidget(self.conditional_props_group)

        self.mode_change_type_spin = QSpinBox()
        self.mode_change_type_spin.setRange(0, 255)  # byte
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

        self.mode_keys_group = QGroupBox("Mode Animation Keys")
        self.mode_keys_layout = QVBoxLayout()
        self.mode_keys_group.setLayout(self.mode_keys_layout)
        self.content_layout.addWidget(self.mode_keys_group)

        add_mode_key_button = QPushButton("Add Mode Animation Key")
        add_mode_key_button.clicked.connect(self.add_mode_animation_key)
        self.content_layout.addWidget(add_mode_key_button)

        self.content_layout.addStretch()
        self.connect_signals()
        self.clear_data()  # Initialize with empty/disabled state
        self.setEnabled(False)  # Initially disabled until data is loaded

    # ... (connect_signals, set_data, clear_data, update_anim_set_data, update_conditional_visibility, populate_mode_animation_keys, add_mode_animation_key, commit_changes methods from previous response)
    # Ensure they are correctly defined within AnimationSetEditorWidget
    def connect_signals(self):
        self.version_spin.valueChanged.connect(
            self.update_anim_set_data_and_visibility
        )  # Changed
        self.revision_spin.valueChanged.connect(
            self.update_anim_set_data_and_visibility
        )  # Changed
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
            # Block signals
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

            self.update_conditional_visibility()  # Call this after setting version/revision
            self.populate_mode_animation_keys()
            self.setEnabled(True)
        else:
            self.clear_data()  # This will also call update_conditional_visibility
            self.setEnabled(False)

    def clear_data(self):
        self.animation_set_data = None
        widgets_to_clear_value = [
            self.version_spin,
            self.revision_spin,
            self.run_speed_spin,
            self.walk_speed_spin,
            self.mode_change_type_spin,
            self.fly_bank_scale_spin,
            self.fly_accel_scale_spin,
            self.fly_hit_scale_spin,
        ]
        for widget in widgets_to_clear_value:
            widget.blockSignals(True)  # Block before clearing
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(widget.minimum() if hasattr(widget, "minimum") else 0)
            widget.blockSignals(False)

        checkboxes_to_clear = [self.hovering_ground_check, self.align_to_terrain_check]
        for checkbox in checkboxes_to_clear:
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)

        while self.mode_keys_layout.count():
            child = self.mode_keys_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.update_conditional_visibility()
        self.setEnabled(False)

    def update_anim_set_data_and_visibility(self):  # Renamed from update_anim_set_data
        if not self.animation_set_data:
            return

        # Update data model first
        self.animation_set_data.version = self.version_spin.value()
        self.animation_set_data.revision = self.revision_spin.value()

        self.log_widget.log_message(
            f"AnimationSet version/revision updated. V: {self.animation_set_data.version}, R: {self.animation_set_data.revision}"
        )
        self.update_conditional_visibility()  # Then update UI visibility

    def update_conditional_visibility(self):
        version_ok = False
        revision_ok_lvl1 = False
        revision_ok_lvl2 = False
        revision_ok_lvl3 = False

        current_version = (
            self.version_spin.value()
        )  # Use current UI value for visibility
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
        # QFormLayout takes care of showing/hiding label for checkbox itself via its row

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

        any_conditional_visible = is_visible_lvl1 or is_visible_lvl2 or is_visible_lvl3
        self.conditional_props_group.setVisible(any_conditional_visible)

    def populate_mode_animation_keys(self):
        while self.mode_keys_layout.count():
            child = self.mode_keys_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self.animation_set_data and self.animation_set_data.mode_animation_keys:
            for mode_key in self.animation_set_data.mode_animation_keys:
                key_widget = ModeAnimationKeyWidget(
                    mode_key, self.animation_set_data, self.drs_handler, self.log_widget
                )
                self.mode_keys_layout.addWidget(key_widget)
            if not self.animation_set_data.mode_animation_keys:  # If list is empty
                self.mode_keys_layout.addWidget(
                    QLabel("No Mode Animation Keys defined. Click 'Add' below.")
                )
        else:
            self.mode_keys_layout.addWidget(
                QLabel("No Mode Animation Keys to display.")
            )

    def add_mode_animation_key(self):
        if not self.animation_set_data:
            self.log_widget.log_message(
                "Cannot add ModeAnimationKey: AnimationSet data not loaded."
            )
            return

        new_key = ModeAnimationKey()
        new_key.file = f"NewKey_{len(self.animation_set_data.mode_animation_keys) + 1}"
        new_key.length = len(new_key.file.encode("utf-8"))
        # Set default type based on AnimationSet version (example, from drs_definitions, ModeAnimationKey.read uk parameter logic)
        if self.animation_set_data.version == 2:
            new_key.type = 2  # Example based on common pattern for v2 if uk=2
        else:
            new_key.type = 6  # Common default

        self.animation_set_data.mode_animation_keys.append(new_key)
        self.animation_set_data.mode_animation_key_count = len(
            self.animation_set_data.mode_animation_keys
        )

        self.log_widget.log_message(f"Added new Mode Animation Key: {new_key.file}")
        self.populate_mode_animation_keys()

    def commit_changes(self):
        if self.animation_set_data:
            self.log_widget.log_message(
                "AnimationSet changes committed to internal data object."
            )
            # Data should be up-to-date via signals.
            # Call update_node_size on the DRS object's animation_set if its size might change.
            # The AnimationSet.size() method should be accurate.
            # self.drs_handler.update_node_size(self.animation_set_data) # if AnimationSet itself is the node data
            if self.drs_handler.drs_object:
                self.drs_handler.update_node_size(
                    self.drs_handler.drs_object.animation_set
                )
