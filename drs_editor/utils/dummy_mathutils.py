# drs_editor/utils/dummy_mathutils.py
class Vector:
    """Dummy Vector class to mimic mathutils.Vector."""

    def __init__(self, values=(0.0, 0.0, 0.0)):
        if isinstance(values, (int, float)):  # For Vector((0,0,0)) vs Vector(size)
            self.values = [float(values)] * 3
        else:
            self.values = [float(v) for v in values]

    def __getitem__(self, index):
        return self.values[index]

    def __setitem__(self, index, value):
        self.values[index] = float(value)

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"Vector({self.values})"


class Matrix:
    """Dummy Matrix class to mimic mathutils.Matrix."""

    def __init__(self, rows=None):
        if rows is None:
            self.rows = [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ]  # Default 3x3
        else:
            self.rows = [[float(v) for v in r] for r in rows]

    def __getitem__(self, index):
        return self.rows[index]

    def __repr__(self):
        return f"Matrix({self.rows})"


class Quaternion:
    """Dummy Quaternion class to mimic mathutils.Quaternion."""

    def __init__(self, values=(1.0, 0.0, 0.0, 0.0)):  # w, x, y, z
        self.values = [float(v) for v in values]

    def __getitem__(self, index):
        return self.values[index]

    def __setitem__(self, index, value):
        self.values[index] = float(value)

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"Quaternion({self.values})"
