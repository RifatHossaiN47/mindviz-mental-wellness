"""
Optional camera-capture dialog for face image input.

Requires opencv-python to be installed (pip install opencv-python).
If OpenCV is not available, CameraDialog still opens but shows an informational
message and allows the user to fall back to file upload.
"""

import base64
from typing import Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QLabel, QMessageBox,
                             QPushButton, QVBoxLayout)

try:
    import cv2  # type: ignore
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False


class CameraDialog(QDialog):
    """
    Opens a live webcam preview and returns the captured frame
    as a base64-encoded JPEG string via ``captured_image_b64``.

    Usage::

        dlg = CameraDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            b64 = dlg.captured_image_b64   # str | None
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📸 Capture Face Photo")
        self.setModal(True)
        self.captured_image_b64: Optional[str] = None
        self._cap = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)
        self._last_frame = None

        self._setup_ui()

        if _CV2_AVAILABLE:
            self._start_camera()
        else:
            self._show_no_cv2_message()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _setup_ui(self):
        self.setFixedSize(680, 540)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Preview / message area
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(640, 440)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(
            "background-color: #1a1a1a; border-radius: 8px; color: white; font-size: 15px;"
        )
        self.preview_label.setText("Initializing camera…")
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # Buttons
        btn_row = QHBoxLayout()

        self.btn_capture = QPushButton("📸  Capture")
        self.btn_capture.setFont(QFont("Arial", 13, QFont.Bold))
        self.btn_capture.setFixedHeight(44)
        self.btn_capture.setEnabled(False)
        self.btn_capture.setStyleSheet(
            "QPushButton { background-color: #2E7D32; color: white; border-radius: 8px; }"
            "QPushButton:hover { background-color: #388E3C; }"
            "QPushButton:disabled { background-color: #AAA; }"
        )
        self.btn_capture.clicked.connect(self._capture)
        btn_row.addWidget(self.btn_capture)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFont(QFont("Arial", 13))
        btn_cancel.setFixedHeight(44)
        btn_cancel.setStyleSheet(
            "QPushButton { background-color: white; border: 2px solid #CCC; border-radius: 8px; }"
            "QPushButton:hover { background-color: #F5F5F5; }"
        )
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        layout.addLayout(btn_row)
        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Camera helpers
    # ------------------------------------------------------------------
    def _start_camera(self):
        """Try to open the default webcam (index 0)."""
        self._cap = cv2.VideoCapture(0)
        if not self._cap.isOpened():
            self.preview_label.setText(
                "⚠️ No camera detected.\n\n"
                "Please use the 'Upload Photo' button on the main screen instead."
            )
            return
        self.btn_capture.setEnabled(True)
        self._timer.start(33)  # ~30 fps

    def _update_frame(self):
        if self._cap is None or not self._cap.isOpened():
            return
        ret, frame = self._cap.read()
        if not ret:
            return

        self._last_frame = frame

        # Convert BGR → RGB → QImage → QPixmap
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img).scaled(
            640, 440, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(pixmap)

    def _capture(self):
        """Encode current frame as JPEG base64 and accept the dialog."""
        if self._last_frame is None:
            QMessageBox.warning(self, "No Frame", "Could not read a frame from the camera.")
            return
        ret, buffer = cv2.imencode(".jpg", self._last_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            QMessageBox.warning(self, "Encode Error", "Failed to encode image.")
            return
        self.captured_image_b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
        self._cleanup()
        self.accept()

    def _show_no_cv2_message(self):
        self.preview_label.setText(
            "opencv-python is not installed.\n\n"
            "Install it with:\n"
            "  pip install opencv-python\n\n"
            "Or use 'Upload Photo' on the main screen\n"
            "to select an image file instead."
        )

    def _cleanup(self):
        self._timer.stop()
        if self._cap is not None and self._cap.isOpened():
            self._cap.release()
        self._cap = None

    def closeEvent(self, event):
        self._cleanup()
        super().closeEvent(event)

    def reject(self):
        self._cleanup()
        super().reject()
