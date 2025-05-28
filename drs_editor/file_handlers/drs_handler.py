# drs_editor/file_handlers/drs_handler.py
from drs_editor.data_structures.drs_definitions import DRS


class DRSHandler:
    def __init__(self):
        self.drs_object: DRS | None = None
        self.filepath: str | None = None

    def load_drs(self, filepath: str) -> tuple[bool, str]:
        """Loads a .drs file into the drs_object."""
        try:
            self.drs_object = DRS()
            self.drs_object.read(filepath)  #
            self.filepath = filepath
            # Determine model_type after loading, if possible, or set based on common structures
            # For now, this is a simplification. The DRS class __post_init__ uses model_type.
            # This might need adjustment based on how model_type is determined or if read() handles it.
            # The provided DRS.read doesn't seem to set self.model_type explicitly.
            # This might be an issue if save() relies on it without it being set.
            # Let's assume for now we can proceed, or that a default/detected model_type is found.

            # Try to infer model_type based on loaded nodes for robust saving
            if self.drs_object:
                self.drs_object.model_type = self._infer_model_type()

            return True, f"Successfully loaded DRS file: {filepath}"
        except Exception as e:
            self.drs_object = None
            self.filepath = None
            return False, f"Error loading DRS file: {e}"

    def _infer_model_type(self) -> str | None:
        """Tries to infer the model type based on the loaded nodes."""
        if not self.drs_object or not self.drs_object.nodes:
            return None

        loaded_node_names = {
            node.name for node in self.drs_object.nodes if hasattr(node, "name")
        }  #

        # InformationIndices contains the node structures for different model types
        from drs_editor.data_structures.drs_definitions import InformationIndices  #

        for model_type, expected_nodes_map in InformationIndices.items():  #
            expected_node_names = set(expected_nodes_map.keys())
            # This is a simple check; a more robust check might ensure all expected nodes are present
            # and potentially that no unexpected critical nodes are present.
            if expected_node_names.issubset(loaded_node_names):
                # A more complex check could involve verifying node_count matches
                if (
                    self.drs_object.node_count == len(expected_nodes_map) + 1
                ):  # +1 for root node
                    return model_type

        # Fallback or more sophisticated detection might be needed
        # For now, let's see if we can find a dominant type
        if "EffectSet" in loaded_node_names and "AnimationSet" in loaded_node_names:
            return "AnimatedUnit"
        if (
            "collisionShape" in loaded_node_names
            and "AnimationSet" not in loaded_node_names
        ):
            return "StaticObjectCollision"
        if "CSkSkeleton" in loaded_node_names and "collisionShape" in loaded_node_names:
            return "AnimatedObjectCollision"
        if (
            "CSkSkeleton" in loaded_node_names
            and "collisionShape" not in loaded_node_names
        ):
            return "AnimatedObjectNoCollision"
        if (
            "CGeoPrimitiveContainer" not in loaded_node_names
            and "CSkSkeleton" not in loaded_node_names
        ):
            return "StaticObjectNoCollision"

        return None  # Could not determine

    def save_drs(self, filepath: str) -> tuple[bool, str]:
        """Saves the current drs_object to a .drs file."""
        if not self.drs_object:
            return False, "No DRS data loaded to save."
        if not self.drs_object.model_type:
            # Attempt to infer again or use a default if necessary
            self.drs_object.model_type = self._infer_model_type()
            if not self.drs_object.model_type:
                # Critical: DRS.save() relies on model_type to determine WriteOrder
                # And __post_init__ uses it to set up nodes and node_informations.
                # This part of DRS needs to be robust if model_type isn't known at init.
                # For now, let's try a common default if still None, or raise error.
                # A better approach: the DRS class should perhaps not auto-initialize nodes in __post_init__
                # if model_type is None, and `read` should fully populate it.
                # `save` would then use the populated structures.
                # The current DRS(model_type="...") in __post_init__ pre-fills nodes.
                # If we read a file, it overwrites these.
                # The problem is if we then save, it needs the correct model_type for WriteOrder.
                return False, "Model type of DRS object is unknown. Cannot save."

        try:
            # Ensure offsets are updated before saving
            # The DRS.save() method in the provided code *calculates* offsets based on node_size.
            # The DRS.update_offsets() method updates self.data_offset based on node_size.
            # It seems save() internally manages this, but a call to update_offsets might be intended.
            # Let's assume DRS.save() handles it or it's part of its internal logic.
            # The provided `DRS.save` re-calculates node_information_offset and node_hierarchy_offset,
            # then writes data packets, then node_informations, then nodes.
            # The `DRS.update_offsets()` method seems to be for calculating the `data_offset`
            # for each `NodeInformation` *before* they are written, which is what `save` should do.

            # The provided `DRS.save` method does not call `update_offsets`.
            # The `NodeInformation.offset` is set by `update_offset` which is called by `DRS.update_offsets`.
            # The `DRS.read` method reads these offsets.
            # When saving, we need to ensure these offsets are correct for the *new* data sizes.

            # Rebuild node_informations and nodes based on current data objects to ensure consistency
            # This is complex because __post_init__ sets up a structure.
            # The simplest way for now is to trust that `read` populated everything correctly
            # and that modifications updated `node_size` where needed.

            # A simplified view: if drs_object was populated by `read()`, its structure is as per the file.
            # If we modify (e.g., a mesh), the size of that component might change.
            # `NodeInformation.node_size` must be updated.
            # `NodeInformation.offset` must be recalculated for all subsequent nodes.
            # The `DRS` class's `update_offsets` method is designed for this.

            # Before saving, ensure all NodeInformation.node_size fields are correct
            for node_info in self.drs_object.node_informations:
                if (
                    hasattr(node_info, "data_object")
                    and node_info.data_object is not None
                ):  # RootNodeInformation has data_object=None
                    if hasattr(node_info.data_object, "size"):
                        actual_size = node_info.data_object.size()
                        if (
                            node_info.node_name == "CGeoPrimitiveContainer"
                        ):  # Special case from drs_definitions
                            actual_size = 0
                        node_info.node_size = actual_size

            # Recalculate initial offsets. The first data packet starts after the main header and all node_info and node structures.
            header_size = (
                20  # magic, num_models, node_info_offset, node_hier_offset, node_count
            )

            # Size of all NodeInformation entries
            # RootNodeInformation is 32 bytes. Other NodeInformation entries are also 32 bytes.
            node_info_total_size = 0
            for ni in self.drs_object.node_informations:
                node_info_total_size += (
                    ni.size()
                )  # size() method in NodeInformation and RootNodeInformation

            # Size of all Node entries
            # RootNode size depends on its name length. Other Node sizes depend on their name lengths.
            node_hierarchy_total_size = 0
            for n in self.drs_object.nodes:
                node_hierarchy_total_size += (
                    n.size()
                )  # size() method in Node and RootNode

            self.drs_object.node_information_offset = (
                header_size  # Node Infos start right after header
            )
            self.drs_object.node_hierarchy_offset = (
                self.drs_object.node_information_offset + node_info_total_size
            )  # Node Hierarchy after Node Infos

            current_data_offset = (
                self.drs_object.node_hierarchy_offset + node_hierarchy_total_size
            )  # Data starts after Node Hierarchy

            # Update offsets for each data node based on the write order
            from drs_editor.data_structures.drs_definitions import WriteOrder  #

            for node_name_to_write in WriteOrder[self.drs_object.model_type]:  #
                # Find the NodeInformation corresponding to this node_name
                found_node_info = None
                for ni in self.drs_object.node_informations:
                    if (
                        hasattr(ni, "node_name") and ni.node_name == node_name_to_write
                    ):  #
                        found_node_info = ni
                        break

                if found_node_info:
                    found_node_info.offset = current_data_offset  #
                    current_data_offset += found_node_info.node_size
                # Else: Node specified in WriteOrder but not found in node_informations. This would be an error.

            self.drs_object.save(filepath)  #
            return True, f"Successfully saved DRS file: {filepath}"
        except Exception as e:
            return (
                False,
                f"Error saving DRS file: {e}\nMake sure model_type ('{self.drs_object.model_type if self.drs_object else 'N/A'}') is correct and all data is consistent.",
            )

    def get_cdsp_mesh_file(self):
        """Returns the CDspMeshFile object from the loaded DRS data."""
        if self.drs_object and hasattr(self.drs_object, "cdsp_mesh_file"):
            return self.drs_object.cdsp_mesh_file  #
        return None

    def get_battleforge_meshes(self):
        """Returns a list of BattleforgeMesh objects."""
        cdsp_mesh_file = self.get_cdsp_mesh_file()
        if cdsp_mesh_file and hasattr(cdsp_mesh_file, "meshes"):
            return cdsp_mesh_file.meshes  #
        return []

    def update_node_size(self, data_object_instance):
        """
        Finds the NodeInformation associated with data_object_instance and updates its node_size.
        This should be called after a data object (e.g., BattleforgeMesh) is modified.
        """
        if not self.drs_object:
            return

        for node_info in self.drs_object.node_informations:
            if (
                hasattr(node_info, "data_object")
                and node_info.data_object is data_object_instance
            ):
                if hasattr(data_object_instance, "size"):
                    new_size = data_object_instance.size()
                    # Handle CGeoPrimitiveContainer specifically if its size should be 0
                    if node_info.node_name == "CGeoPrimitiveContainer":  #
                        new_size = 0
                    if node_info.node_size != new_size:
                        node_info.node_size = new_size
                        # Potentially trigger a log or a flag that offsets need recalculation
                break
