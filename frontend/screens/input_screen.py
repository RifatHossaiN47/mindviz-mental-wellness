from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class InputScreen(QWidget):
    def __init__(self, username="Guest", parent=None):
        super().__init__()
        self.app = parent
        self.username = username
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
    
    def analyze_state(self):
        user_text = self.text_input.toPlainText().strip()
        if not user_text:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Empty Input", "Please share how you're feeling before analyzing.")
            return
        
        # Show loading screen
        self.app.show_loading_screen(user_text, self.username)
    
    def show_journey(self):
        self.app.show_journey_screen(self.username)
    
    def logout(self):
        self.app.show_welcome_screen()
