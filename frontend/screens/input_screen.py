import base64
import os
from typing import Optional

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QSpacerItem, QSizePolicy,
                             QCheckBox, QFileDialog, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap

_FACE_DISCLAIMER = (
    "ℹ️  Face analysis is optional and provides only a non-diagnostic wellness indicator. "
    "It is NOT a medical diagnosis. Images are sent only to the Gemini API for analysis "
    "and are never stored on disk."
)

_MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB guard


class InputScreen(QWidget):
    def __init__(self, username="Guest", parent=None):
        super().__init__()
        self.app = parent
        self.username = username
        self.face_image_b64: Optional[str] = None  # set when user provides a photo
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Header with username
        header_layout = QHBoxLayout()
        
        header = QLabel(f"🌱 MindViz")
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet("color: #2E7D32;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        user_label = QLabel(f"Welcome, {self.username}!")
        user_label.setFont(QFont("Arial", 14))
        user_label.setStyleSheet("color: #555;")
        header_layout.addWidget(user_label)
        
        layout.addLayout(header_layout)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Question
        question = QLabel("How are you feeling right now?")
        question.setFont(QFont("Arial", 22, QFont.Bold))
        question.setAlignment(Qt.AlignCenter)
        question.setStyleSheet("color: #333;")
        layout.addWidget(question)
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Share your feelings here...\n\n"
            "For example:\n"
            "• I'm feeling stressed about my assignments\n"
            "• I have 3 projects due and feel overwhelmed\n"
            "• I'm anxious about my upcoming exams"
        )
        self.text_input.setFont(QFont("Arial", 14))
        self.text_input.setMinimumHeight(180)
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #DDD;
                border-radius: 10px;
                padding: 15px;
                background-color: white;
            }
            QTextEdit:focus {
                border: 2px solid #2E7D32;
            }
        """)
        layout.addWidget(self.text_input)
        
        # Quick emoji buttons
        emoji_label = QLabel("Quick options:")
        emoji_label.setFont(QFont("Arial", 13))
        emoji_label.setStyleSheet("color: #666;")
        layout.addWidget(emoji_label)
        
        emoji_layout = QHBoxLayout()
        emoji_layout.setSpacing(10)
        
        emojis = [
            ("😰 Anxious", "I'm feeling very anxious and worried right now. My mind is racing with concerns."),
            ("😔 Sad", "I'm feeling sad and down. My mood is quite low today."),
            ("😤 Stressed", "I'm feeling stressed and overwhelmed with everything I need to do."),
            ("😊 Good", "I'm feeling good and positive! Things are going well.")
        ]
        
        for emoji, text in emojis:
            btn = QPushButton(emoji)
            btn.setFont(QFont("Arial", 12))
            btn.setFixedHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #DDD;
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #E8F5E9;
                    border-color: #2E7D32;
                }
            """)
            btn.clicked.connect(lambda checked, t=text: self.set_quick_text(t))
            emoji_layout.addWidget(btn)
        
        layout.addLayout(emoji_layout)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ── Optional Face Image Section ─────────────────────────────────────
        face_frame = QFrame()
        face_frame.setStyleSheet(
            "QFrame { border: 1px solid #DDD; border-radius: 10px; background-color: #FAFAFA; }"
        )
        face_layout = QVBoxLayout(face_frame)
        face_layout.setSpacing(8)
        face_layout.setContentsMargins(14, 12, 14, 12)

        # Consent checkbox
        self.consent_checkbox = QCheckBox(
            "Optional: include my face photo to improve wellness analysis"
        )
        self.consent_checkbox.setFont(QFont("Arial", 12))
        self.consent_checkbox.setStyleSheet("QCheckBox { border: none; background: transparent; }")
        self.consent_checkbox.toggled.connect(self._on_consent_toggled)
        face_layout.addWidget(self.consent_checkbox)

        # Disclaimer label
        disclaimer_label = QLabel(_FACE_DISCLAIMER)
        disclaimer_label.setFont(QFont("Arial", 10))
        disclaimer_label.setStyleSheet("color: #777; border: none; background: transparent;")
        disclaimer_label.setWordWrap(True)
        face_layout.addWidget(disclaimer_label)

        # Divider
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #EEE; border: none; max-height: 1px;")
        face_layout.addWidget(sep)

        # Capture buttons row + thumbnail
        capture_row = QHBoxLayout()

        self.btn_upload = QPushButton("📁  Upload Photo")
        self.btn_upload.setFont(QFont("Arial", 12))
        self.btn_upload.setFixedHeight(40)
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        self.btn_upload.setEnabled(False)
        self.btn_upload.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #BBB;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #E8F5E9; border-color: #2E7D32; }
            QPushButton:disabled { color: #AAA; border-color: #DDD; }
        """)
        self.btn_upload.clicked.connect(self._upload_photo)
        capture_row.addWidget(self.btn_upload)

        self.btn_camera = QPushButton("📸  Camera")
        self.btn_camera.setFont(QFont("Arial", 12))
        self.btn_camera.setFixedHeight(40)
        self.btn_camera.setCursor(Qt.PointingHandCursor)
        self.btn_camera.setEnabled(False)
        self.btn_camera.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #BBB;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #E8F5E9; border-color: #2E7D32; }
            QPushButton:disabled { color: #AAA; border-color: #DDD; }
        """)
        self.btn_camera.clicked.connect(self._open_camera)
        capture_row.addWidget(self.btn_camera)

        self.btn_clear_photo = QPushButton("✕  Clear")
        self.btn_clear_photo.setFont(QFont("Arial", 11))
        self.btn_clear_photo.setFixedHeight(40)
        self.btn_clear_photo.setCursor(Qt.PointingHandCursor)
        self.btn_clear_photo.setVisible(False)
        self.btn_clear_photo.setStyleSheet(
            "QPushButton { background-color: white; border: 2px solid #EEEEAA; border-radius: 8px; }"
            "QPushButton:hover { background-color: #FFF8E1; }"
        )
        self.btn_clear_photo.clicked.connect(self._clear_photo)
        capture_row.addWidget(self.btn_clear_photo)

        capture_row.addStretch()

        # Tiny thumbnail (shown once a photo is loaded)
        self.photo_thumbnail = QLabel()
        self.photo_thumbnail.setFixedSize(64, 64)
        self.photo_thumbnail.setAlignment(Qt.AlignCenter)
        self.photo_thumbnail.setStyleSheet(
            "border: 1px solid #CCC; border-radius: 6px; background: #EEE;"
        )
        self.photo_thumbnail.setVisible(False)
        capture_row.addWidget(self.photo_thumbnail)

        face_layout.addLayout(capture_row)

        # Status text
        self.photo_status = QLabel("No photo selected.")
        self.photo_status.setFont(QFont("Arial", 11))
        self.photo_status.setStyleSheet("color: #888; border: none; background: transparent;")
        face_layout.addWidget(self.photo_status)

        layout.addWidget(face_frame)
        # ── End Face Image Section ───────────────────────────────────────────

        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Analyze button (big and prominent)
        btn_analyze = QPushButton("ANALYZE MY STATE ➜")
        btn_analyze.setFont(QFont("Arial", 18, QFont.Bold))
        btn_analyze.setFixedHeight(70)
        btn_analyze.setCursor(Qt.PointingHandCursor)
        btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)
        btn_analyze.clicked.connect(self.analyze_state)
        layout.addWidget(btn_analyze)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        
        btn_journey = QPushButton("📊 View My Journey")
        btn_journey.setFont(QFont("Arial", 13))
        btn_journey.setFixedHeight(45)
        btn_journey.setCursor(Qt.PointingHandCursor)
        btn_journey.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2E7D32;
                border: 2px solid #2E7D32;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
        """)
        btn_journey.clicked.connect(self.show_journey)
        bottom_layout.addWidget(btn_journey)
        
        btn_logout = QPushButton("Logout")
        btn_logout.setFont(QFont("Arial", 13))
        btn_logout.setFixedHeight(45)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #777;
                border: 2px solid #CCC;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #999;
            }
        """)
        btn_logout.clicked.connect(self.logout)
        bottom_layout.addWidget(btn_logout)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        # Background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#FAFAFA"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
    
    def set_quick_text(self, text):
        self.text_input.setText(text)
        self.text_input.setFocus()

    # ── Face image helpers ───────────────────────────────────────────────
    def _on_consent_toggled(self, checked: bool):
        """Enable/disable capture buttons based on consent checkbox."""
        self.btn_upload.setEnabled(checked)
        self.btn_camera.setEnabled(checked)
        if not checked:
            self._clear_photo()

    def _upload_photo(self):
        """Open a file dialog to select an image file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Face Photo",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.webp)",
        )
        if not path:
            return
        self._load_image_from_path(path)

    def _open_camera(self):
        """Open the camera dialog to capture a live frame."""
        from screens.camera_dialog import CameraDialog
        from PyQt5.QtWidgets import QDialog

        dlg = CameraDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted and dlg.captured_image_b64:
            self.face_image_b64 = dlg.captured_image_b64
            self._show_thumbnail_from_b64(self.face_image_b64)
            self.photo_status.setText("✅  Camera photo ready.")
            self.btn_clear_photo.setVisible(True)

    def _load_image_from_path(self, path: str):
        """Read an image file, validate size, encode to base64, show thumbnail."""
        try:
            size = os.path.getsize(path)
            if size > _MAX_IMAGE_BYTES:
                QMessageBox.warning(
                    self,
                    "File Too Large",
                    "Please choose an image smaller than 5 MB.",
                )
                return
            with open(path, "rb") as fh:
                raw = fh.read()
            self.face_image_b64 = base64.b64encode(raw).decode("utf-8")
            self._show_thumbnail_from_b64(self.face_image_b64)
            fname = os.path.basename(path)
            self.photo_status.setText(f"✅  Photo ready: {fname}")
            self.btn_clear_photo.setVisible(True)
        except Exception as exc:
            QMessageBox.warning(self, "Load Error", f"Could not load image:\n{exc}")

    def _show_thumbnail_from_b64(self, b64: str):
        """Render a 64×64 thumbnail from a base64 string."""
        try:
            raw = base64.b64decode(b64)
            pixmap = QPixmap()
            pixmap.loadFromData(raw)
            self.photo_thumbnail.setPixmap(
                pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.photo_thumbnail.setVisible(True)
        except Exception:
            self.photo_thumbnail.setVisible(False)

    def _clear_photo(self):
        """Remove any captured/uploaded image."""
        self.face_image_b64 = None
        self.photo_thumbnail.setVisible(False)
        self.btn_clear_photo.setVisible(False)
        self.photo_status.setText("No photo selected.")

    # ── Main action ──────────────────────────────────────────────────────
    def analyze_state(self):
        user_text = self.text_input.toPlainText().strip()
        if not user_text:
            QMessageBox.warning(self, "Empty Input", "Please share how you're feeling before analyzing.")
            return

        face_consent = self.consent_checkbox.isChecked()
        face_image_b64 = self.face_image_b64 if face_consent else None

        # Show loading screen
        self.app.show_loading_screen(
            user_text,
            self.username,
            face_image_b64=face_image_b64,
            face_consent=face_consent,
        )

    def show_journey(self):
        self.app.show_journey_screen(self.username)

    def logout(self):
        self.app.show_welcome_screen()
