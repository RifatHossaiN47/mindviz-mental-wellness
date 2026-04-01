from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpacerItem, QSizePolicy, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor


class GameModeScreen(QWidget):
    def __init__(self, username="Guest", parent=None):
        super().__init__()
        self.app = parent
        self.username = username
        self.selected_duration = 2
        self.duration_buttons = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        # Header
        header_layout = QHBoxLayout()

        header = QLabel("🌱 MindViz")
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet("color: #2E7D32;")
        header_layout.addWidget(header)

        header_layout.addStretch()

        subtitle = QLabel("No Writing Needed")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #555;")
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        layout.addSpacerItem(QSpacerItem(20, 35, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Main heading
        heading = QLabel("How long do you want to play?")
        heading.setFont(QFont("Arial", 28, QFont.Bold))
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet("color: #333;")
        layout.addWidget(heading)

        subtext = QLabel("We'll analyze your gameplay to understand your mental state.")
        subtext.setFont(QFont("Arial", 14))
        subtext.setAlignment(Qt.AlignCenter)
        subtext.setStyleSheet("color: #666;")
        layout.addWidget(subtext)

        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Duration toggles
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(12)
        duration_layout.setAlignment(Qt.AlignCenter)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        for minutes in [1, 2, 3, 4, 5]:
            btn = QPushButton(f"{minutes} min")
            btn.setCheckable(True)
            btn.setFont(QFont("Arial", 13, QFont.Bold))
            btn.setFixedSize(105, 52)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #2E7D32;
                    border: 2px solid #2E7D32;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #E8F5E9;
                }
                QPushButton:checked {
                    background-color: #2E7D32;
                    color: white;
                    border: 2px solid #2E7D32;
                }
            """)
            btn.clicked.connect(lambda checked, m=minutes: self.select_duration(m))
            self.button_group.addButton(btn)
            self.duration_buttons[minutes] = btn
            duration_layout.addWidget(btn)

        layout.addLayout(duration_layout)

        # Default selection
        self.duration_buttons[self.selected_duration].setChecked(True)

        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Description
        description = QLabel(
            "Pop the bubbles at your own pace. Your reaction patterns reveal your\n"
            "current emotional state."
        )
        description.setFont(QFont("Arial", 12))
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #777;")
        layout.addWidget(description)

        layout.addSpacerItem(QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Primary action
        btn_start = QPushButton("START GAME")
        btn_start.setFont(QFont("Arial", 18, QFont.Bold))
        btn_start.setFixedHeight(70)
        btn_start.setCursor(Qt.PointingHandCursor)
        btn_start.setStyleSheet("""
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
        btn_start.clicked.connect(self.start_game)
        layout.addWidget(btn_start)

        layout.addStretch()

        # Footer back button
        footer_layout = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.setFont(QFont("Arial", 12))
        btn_back.setFixedHeight(40)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #777;
                border: 2px solid #CCC;
                border-radius: 8px;
                padding: 0 14px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #999;
            }
        """)
        btn_back.clicked.connect(self.go_back)
        footer_layout.addWidget(btn_back, alignment=Qt.AlignLeft)
        footer_layout.addStretch()

        layout.addLayout(footer_layout)

        self.setLayout(layout)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#FAFAFA"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def select_duration(self, minutes):
        self.selected_duration = minutes

    def start_game(self):
        self.app.show_game_screen(self.username, self.selected_duration)

    def go_back(self):
        self.app.show_welcome_screen()
