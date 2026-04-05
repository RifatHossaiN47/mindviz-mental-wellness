from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QSpacerItem, QSizePolicy,
                             QCheckBox, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QImage, QPixmap

# Optional OpenCV import — camera section is hidden gracefully if unavailable
try:
    import cv2
    import base64
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class InputScreen(QWidget):
    def __init__(self, username="Guest", parent=None):
        super().__init__()
        self.app = parent
        self.username = username
        self._camera = None          # cv2.VideoCapture instance
        self._camera_timer = None    # QTimer for live feed
        self._captured_image_b64 = None  # base64 JPEG of captured frame
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
        
        # ── Main content row: text input + camera section ───────────────────────
        content_row = QHBoxLayout()
        content_row.setSpacing(20)
        
        # Left: text input
        text_col = QVBoxLayout()
        
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
        text_col.addWidget(self.text_input)
        
        content_row.addLayout(text_col, stretch=3)
        
        # Right: camera section
        self._camera_section = self._build_camera_section()
        content_row.addWidget(self._camera_section, stretch=2)
        
        layout.addLayout(content_row)
        
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

    # ── Camera section builder ────────────────────────────────────────────────

    def _build_camera_section(self) -> QFrame:
        """Build the optional face-capture panel and return it as a QFrame."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 2px solid #DDD;
                border-radius: 10px;
                background-color: white;
                padding: 4px;
            }
        """)
        vbox = QVBoxLayout(frame)
        vbox.setSpacing(8)
        vbox.setContentsMargins(10, 10, 10, 10)

        # Section title
        title = QLabel("📷 Face Analysis  (optional)")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        title.setStyleSheet("color: #2E7D32; border: none;")
        vbox.addWidget(title)

        if not CV2_AVAILABLE:
            # OpenCV not installed — show informational message only
            msg = QLabel(
                "Camera feature requires opencv-python.\n"
                "Install it to enable face analysis:\n\n"
                "  pip install opencv-python"
            )
            msg.setFont(QFont("Arial", 11))
            msg.setStyleSheet("color: #888; border: none;")
            msg.setWordWrap(True)
            vbox.addWidget(msg)
            vbox.addStretch()
            return frame

        # Camera preview label
        self._preview_label = QLabel()
        self._preview_label.setFixedSize(240, 180)
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setStyleSheet(
            "border: 1px solid #CCC; border-radius: 6px; "
            "background-color: #F0F0F0; color: #999;"
        )
        self._preview_label.setText("Camera inactive")
        vbox.addWidget(self._preview_label, alignment=Qt.AlignCenter)

        # Camera control buttons
        cam_btn_row = QHBoxLayout()
        cam_btn_row.setSpacing(6)

        btn_style = """
            QPushButton {
                background-color: #F5F5F5;
                border: 1px solid #CCC;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #E8F5E9; border-color: #2E7D32; }
            QPushButton:disabled { color: #BBB; background-color: #FAFAFA; }
        """

        self._btn_start_camera = QPushButton("▶ Start")
        self._btn_start_camera.setFont(QFont("Arial", 11))
        self._btn_start_camera.setFixedHeight(34)
        self._btn_start_camera.setCursor(Qt.PointingHandCursor)
        self._btn_start_camera.setStyleSheet(btn_style)
        self._btn_start_camera.clicked.connect(self._start_camera)
        cam_btn_row.addWidget(self._btn_start_camera)

        self._btn_capture = QPushButton("📸 Capture")
        self._btn_capture.setFont(QFont("Arial", 11))
        self._btn_capture.setFixedHeight(34)
        self._btn_capture.setCursor(Qt.PointingHandCursor)
        self._btn_capture.setStyleSheet(btn_style)
        self._btn_capture.setEnabled(False)
        self._btn_capture.clicked.connect(self._capture_frame)
        cam_btn_row.addWidget(self._btn_capture)

        self._btn_retake = QPushButton("↺ Retake")
        self._btn_retake.setFont(QFont("Arial", 11))
        self._btn_retake.setFixedHeight(34)
        self._btn_retake.setCursor(Qt.PointingHandCursor)
        self._btn_retake.setStyleSheet(btn_style)
        self._btn_retake.setEnabled(False)
        self._btn_retake.clicked.connect(self._retake)
        cam_btn_row.addWidget(self._btn_retake)

        vbox.addLayout(cam_btn_row)

        # "Use face analysis" toggle
        self._face_toggle = QCheckBox("Use face analysis")
        self._face_toggle.setFont(QFont("Arial", 12))
        self._face_toggle.setChecked(False)
        self._face_toggle.setStyleSheet("border: none; color: #333;")
        self._face_toggle.setToolTip(
            "When checked, your captured face image will be analyzed\n"
            "alongside your text to improve the wellness assessment."
        )
        vbox.addWidget(self._face_toggle)

        # Consent / disclaimer notice
        consent = QLabel(
            "🔒 By enabling camera you agree to analyze facial\n"
            "expressions locally for wellness insights only.\n"
            "Images are not stored or shared."
        )
        consent.setFont(QFont("Arial", 10))
        consent.setStyleSheet("color: #888; border: none;")
        consent.setWordWrap(True)
        vbox.addWidget(consent)

        # Disclaimer
        disclaimer = QLabel("ⓘ This is a wellness aid, not a medical diagnosis.")
        disclaimer.setFont(QFont("Arial", 10))
        disclaimer.setStyleSheet("color: #AAA; border: none;")
        disclaimer.setWordWrap(True)
        vbox.addWidget(disclaimer)

        vbox.addStretch()
        return frame

    # ── Camera helpers ────────────────────────────────────────────────────────

    def _start_camera(self):
        """Open the default webcam and start streaming frames."""
        if not CV2_AVAILABLE:
            return
        try:
            self._camera = cv2.VideoCapture(0)
            if not self._camera.isOpened():
                self._preview_label.setText("Camera not available")
                return

            self._btn_start_camera.setEnabled(False)
            self._btn_capture.setEnabled(True)
            self._face_toggle.setChecked(True)

            self._camera_timer = QTimer(self)
            self._camera_timer.timeout.connect(self._update_preview)
            self._camera_timer.start(33)  # ~30 fps
        except Exception as exc:
            print(f"[CAMERA] Error opening camera: {exc}")
            self._preview_label.setText("Camera error")

    def _update_preview(self):
        """Read one frame and refresh the preview label."""
        if self._camera is None or not self._camera.isOpened():
            return
        ret, frame = self._camera.read()
        if not ret:
            return
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        qt_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qt_img)
        self._preview_label.setPixmap(
            pix.scaled(240, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def _capture_frame(self):
        """Capture the current frame, encode as base64, and freeze preview."""
        if self._camera is None or not self._camera.isOpened():
            return
        ret, frame = self._camera.read()
        if not ret:
            return

        # Stop live feed
        if self._camera_timer:
            self._camera_timer.stop()
        self._camera.release()
        self._camera = None

        # Encode to JPEG base64
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        self._captured_image_b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")

        # Show frozen preview with a visual indicator
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        qt_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qt_img)
        self._preview_label.setPixmap(
            pix.scaled(240, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        self._btn_capture.setEnabled(False)
        self._btn_retake.setEnabled(True)
        print("[CAMERA] Frame captured successfully")

    def _retake(self):
        """Discard the captured image and re-open the camera."""
        self._captured_image_b64 = None
        self._btn_retake.setEnabled(False)
        self._btn_capture.setEnabled(False)
        self._btn_start_camera.setEnabled(True)
        self._preview_label.setText("Camera inactive")
        self._preview_label.setPixmap(QPixmap())

    def _stop_camera(self):
        """Release camera resources — called on screen teardown."""
        if self._camera_timer:
            self._camera_timer.stop()
            self._camera_timer = None
        if self._camera and self._camera.isOpened():
            self._camera.release()
            self._camera = None

    def hideEvent(self, event):
        """Release camera when screen is hidden/removed."""
        self._stop_camera()
        super().hideEvent(event)

    def closeEvent(self, event):
        self._stop_camera()
        super().closeEvent(event)

    # ── Existing helpers ──────────────────────────────────────────────────────

    def set_quick_text(self, text):
        self.text_input.setText(text)
        self.text_input.setFocus()
    
    def analyze_state(self):
        user_text = self.text_input.toPlainText().strip()
        if not user_text:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Empty Input", "Please share how you're feeling before analyzing.")
            return
        
        # Collect face image if capture is enabled and available
        face_image = None
        if CV2_AVAILABLE and hasattr(self, "_face_toggle") and self._face_toggle.isChecked():
            if self._captured_image_b64:
                face_image = self._captured_image_b64
            else:
                from PyQt5.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "No Face Image Captured",
                    "Face analysis is enabled but no image was captured.\n\n"
                    "Continue with text-only analysis?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )
                if reply == QMessageBox.No:
                    return

        # Release camera before leaving screen
        self._stop_camera()
        
        # Show loading screen (pass face image if available)
        self.app.show_loading_screen(user_text, self.username, face_image=face_image)
    
    def show_journey(self):
        self._stop_camera()
        self.app.show_journey_screen(self.username)
    
    def logout(self):
        self._stop_camera()
        self.app.show_welcome_screen()
