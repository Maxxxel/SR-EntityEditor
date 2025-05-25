# drs_editor/gui/editors/texture_preview_dialog.py
import os
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QRadioButton,
    QHBoxLayout,
    QButtonGroup,
    QWidget,
    QScrollArea,
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from PIL import Image, ImageQt


class TexturePreviewDialog(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            f"Texture Preview - {os.path.basename(image_path)}"
        )  # Show only filename
        self.setMinimumSize(500, 550)  # Increased size a bit

        self.pil_image_original: Image.Image | None = None
        self.image_path = image_path

        main_layout = QVBoxLayout(self)

        # Use QScrollArea for the image label to handle images larger than the label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(
            True
        )  # Important for the label to resize correctly
        self.image_label = QLabel("Loading preview...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)  # Put label in scroll area
        main_layout.addWidget(self.scroll_area)

        channel_widget = QWidget()
        channel_layout = QHBoxLayout(channel_widget)
        self.channel_group = QButtonGroup(self)

        rb_all = QRadioButton("All")
        rb_r = QRadioButton("Red")
        rb_g = QRadioButton("Green")
        rb_b = QRadioButton("Blue")
        rb_a = QRadioButton("Alpha")

        self.channel_buttons = {
            "All": rb_all,
            "R": rb_r,
            "G": rb_g,
            "B": rb_b,
            "A": rb_a,
        }

        for rb in self.channel_buttons.values():  # Corrected iteration
            channel_layout.addWidget(rb)
            self.channel_group.addButton(rb)
            rb.toggled.connect(self.on_channel_selected)  # Connect to a handler

        main_layout.addWidget(channel_widget)
        self.channel_buttons["All"].setChecked(True)

        self.load_image_and_display()

    def load_image_and_display(self):
        try:
            self.pil_image_original = Image.open(self.image_path)
            # Ensure the image is in a mode we can easily work with (RGBA)
            if self.pil_image_original.mode != "RGBA":
                self.pil_image_original = self.pil_image_original.convert("RGBA")

            self.display_image()  # Display "All" channels first
        except FileNotFoundError:
            self.image_label.setText(f"File not found: {self.image_path}")
            self.disable_channel_buttons()
        except Exception as e:
            self.image_label.setText(
                f"Error loading image: {e}\n(Ensure Pillow supports this DDS format)"
            )
            print(f"Error loading image {self.image_path}: {e}")
            self.disable_channel_buttons()

    def disable_channel_buttons(self):
        for btn in self.channel_buttons.values():
            btn.setEnabled(False)

    def on_channel_selected(self):
        # This slot is called when a radio button is toggled.
        # We only care about the one that becomes checked.
        checked_button = self.channel_group.checkedButton()
        if checked_button and checked_button.isChecked():
            self.display_image()

    def display_image(self):
        if not self.pil_image_original:
            return

        selected_button = self.channel_group.checkedButton()
        if not selected_button:
            channel_mode = "All"  # Default if somehow none is selected
        else:
            channel_mode = selected_button.text()

        # It's crucial to work on a copy if manipulations are destructive
        # or if the original split channels are needed elsewhere.
        # For merging, we create new images, so original channels from split() are fine.

        try:
            # Ensure original is RGBA after loading
            if self.pil_image_original.mode != "RGBA":
                # This should have been handled in load_image_and_display, but as a safeguard:
                temp_img = self.pil_image_original.convert("RGBA")
                r, g, b, a = temp_img.split()
            else:
                r, g, b, a = self.pil_image_original.split()

            # Create a fully opaque alpha channel for R, G, B views if original alpha is distracting
            opaque_alpha = Image.new("L", self.pil_image_original.size, 255)

            processed_image_pil = None

            if channel_mode == "All":
                processed_image_pil = (
                    self.pil_image_original
                )  # Show the original (converted to RGBA)
            elif channel_mode == "Red":
                # Red channel opaque red, others black, use original alpha for shape
                processed_image_pil = Image.merge(
                    "RGBA", (r, Image.new("L", r.size, 0), Image.new("L", r.size, 0), a)
                )
            elif channel_mode == "Green":
                processed_image_pil = Image.merge(
                    "RGBA", (Image.new("L", g.size, 0), g, Image.new("L", g.size, 0), a)
                )
            elif channel_mode == "Blue":
                processed_image_pil = Image.merge(
                    "RGBA", (Image.new("L", b.size, 0), Image.new("L", b.size, 0), b, a)
                )
            elif channel_mode == "Alpha":
                # Show alpha as grayscale, fully opaque (so grayscale is visible)
                processed_image_pil = Image.merge("RGBA", (a, a, a, opaque_alpha))
            else:  # Should not happen
                processed_image_pil = self.pil_image_original

            if processed_image_pil:
                qimage = ImageQt.ImageQt(processed_image_pil)
                pixmap = QPixmap.fromImage(qimage)

                # --- Fix for shrinking image ---
                # Scale the pixmap to fit the scroll_area's viewport size,
                # or a fixed reasonable preview size if the image is smaller.
                # Using the scroll_area.viewport().size() ensures we scale based on available space.

                # Use a fixed maximum preview size to prevent overly large images from slowing things down
                # or making the dialog huge if scroll_area is not constrained.
                max_preview_width = max(self.pil_image_original.width, 512)
                max_preview_height = max(self.pil_image_original.height, 512)

                # If dialog is resizable, image_label size might be small initially.
                # Option 1: Give image_label a fixed large enough size, or ensure scroll_area constrains it.
                # Option 2: Scale to original image size but cap it.

                # Let's scale to fit within a reasonable area of the dialog, maintaining aspect ratio.
                # The self.image_label is inside a QScrollArea with setWidgetResizable(True).
                # So, the label will try to take available space.
                # We should scale the pixmap to fit the viewport of the scroll area.

                viewport_size = self.scroll_area.viewport().size()
                scaled_pixmap = pixmap.scaled(
                    viewport_size,  # Scale to the available space in viewport
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Could not process channel view.")

        except Exception as e:
            self.image_label.setText(f"Error processing channel view: {e}")
            print(f"Error processing channel view for {self.image_path}: {e}")
