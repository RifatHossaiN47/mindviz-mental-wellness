from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
import base64
import cv2


class CameraCaptureDialog(QDialog):
    """Simple webcam dialog for capturing a single face image."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Capture Face Image")
        self.setModal(True)
        self.setMinimumSize(760, 620)

        self.camera = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)

        self.current_frame = None
        self.captured_frame = None

        self._setup_ui()
        self._start_camera()

    def _setup_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QLabel("Center your face and capture a clear image")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E7D32;")
        root.addWidget(title)

        self.video_label = QLabel("Starting camera...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(720, 480)
        self.video_label.setStyleSheet(
            "background-color: #111; color: #EEE; border: 2px solid #444; border-radius: 8px;"
        )
        root.addWidget(self.video_label)

        self.status_label = QLabel("Live preview")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        root.addWidget(self.status_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.capture_btn = QPushButton("Capture")
        self.capture_btn.setCursor(Qt.PointingHandCursor)
        self.capture_btn.setStyleSheet(
            "QPushButton { background-color: #2E7D32; color: white; border: none; border-radius: 6px; padding: 10px 16px; }"
            "QPushButton:hover { background-color: #388E3C; }"
        )
        self.capture_btn.clicked.connect(self._capture_photo)
        btn_row.addWidget(self.capture_btn)

        self.retake_btn = QPushButton("Retake")
        self.retake_btn.setCursor(Qt.PointingHandCursor)
        self.retake_btn.setEnabled(False)
        self.retake_btn.setStyleSheet(
            "QPushButton { background-color: #FB8C00; color: white; border: none; border-radius: 6px; padding: 10px 16px; }"
            "QPushButton:hover { background-color: #EF6C00; }"
            "QPushButton:disabled { background-color: #CCC; color: #888; }"
        )
        self.retake_btn.clicked.connect(self._retake_photo)
        btn_row.addWidget(self.retake_btn)

        self.use_btn = QPushButton("Use Photo")
        self.use_btn.setCursor(Qt.PointingHandCursor)
        self.use_btn.setEnabled(False)
        self.use_btn.setStyleSheet(
            "QPushButton { background-color: #1976D2; color: white; border: none; border-radius: 6px; padding: 10px 16px; }"
            "QPushButton:hover { background-color: #1565C0; }"
            "QPushButton:disabled { background-color: #CCC; color: #888; }"
        )
        self.use_btn.clicked.connect(self._accept_photo)
        btn_row.addWidget(self.use_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setStyleSheet(
            "QPushButton { background-color: #EEEEEE; color: #333; border: 1px solid #CCC; border-radius: 6px; padding: 10px 16px; }"
            "QPushButton:hover { background-color: #E0E0E0; }"
        )
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        root.addLayout(btn_row)
        self.setLayout(root)

    def _start_camera(self):
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            QMessageBox.critical(self, "Camera Error", "Could not access webcam.")
            self.reject()
            return

        self.timer.start(30)

    def _update_frame(self):
        if self.camera is None:
            return

        ok, frame = self.camera.read()
        if not ok:
            return

        self.current_frame = frame
        self._show_frame(frame)

    def _show_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        scaled = pix.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.video_label.setPixmap(scaled)

    def _capture_photo(self):
        if self.current_frame is None:
            QMessageBox.warning(self, "Capture Error", "No frame available yet.")
            return

        self.captured_frame = self.current_frame.copy()
        self.timer.stop()
        self._show_frame(self.captured_frame)

        self.status_label.setText("Photo captured. Use photo or retake.")
        self.capture_btn.setEnabled(False)
        self.retake_btn.setEnabled(True)
        self.use_btn.setEnabled(True)

    def _retake_photo(self):
        self.captured_frame = None
        self.capture_btn.setEnabled(True)
        self.retake_btn.setEnabled(False)
        self.use_btn.setEnabled(False)
        self.status_label.setText("Live preview")

        if self.camera is not None and self.camera.isOpened():
            self.timer.start(30)

    def _accept_photo(self):
        if self.captured_frame is None:
            QMessageBox.warning(self, "No Photo", "Capture a photo first.")
            return
        self.accept()

    def get_image_base64(self):
        if self.captured_frame is None:
            return None

        # Encode as JPEG with moderate quality for smaller payload size.
        ok, buf = cv2.imencode(
            ".jpg",
            self.captured_frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 90],
        )
        if not ok:
            return None

        encoded = base64.b64encode(buf.tobytes()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"

    def closeEvent(self, event):
        try:
            self.timer.stop()
            if self.camera is not None:
                self.camera.release()
        except Exception:
            pass
        super().closeEvent(event)
