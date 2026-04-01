from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import json
import hashlib
import os
from datetime import datetime

# Get the base project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

class AuthScreen(QWidget):
    def __init__(self, mode="signin", parent=None):
        super().__init__()
        self.app = parent
        self.mode = mode
        self.users_file = os.path.join(DATA_DIR, "users.json")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Back button at top
        btn_back = QPushButton("← Back")
        btn_back.setFixedWidth(100)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #2E7D32;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                color: #388E3C;
            }
        """)
        btn_back.clicked.connect(self.go_back)
        layout.addWidget(btn_back, alignment=Qt.AlignLeft)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Title
        title_text = "Sign In" if self.mode == "signin" else "Create Account"
        title = QLabel(title_text)
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E7D32;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle_text = "Welcome back!" if self.mode == "signin" else "Join MindViz today"
        subtitle = QLabel(subtitle_text)
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #777;")
        layout.addWidget(subtitle)
        
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont("Arial", 14))
        self.username_input.setFixedSize(350, 45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #DDD;
                border-radius: 8px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #2E7D32;
            }
        """)
        layout.addWidget(self.username_input, alignment=Qt.AlignCenter)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 14))
        self.password_input.setFixedSize(350, 45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #DDD;
                border-radius: 8px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #2E7D32;
            }
        """)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)
        
        # Confirm password (only for signup)
        if self.mode == "signup":
            self.confirm_input = QLineEdit()
            self.confirm_input.setPlaceholderText("Confirm Password")
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setFont(QFont("Arial", 14))
            self.confirm_input.setFixedSize(350, 45)
            self.confirm_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #DDD;
                    border-radius: 8px;
                    padding: 10px;
                }
                QLineEdit:focus {
                    border: 2px solid #2E7D32;
                }
            """)
            layout.addWidget(self.confirm_input, alignment=Qt.AlignCenter)
        
        # Submit button
        btn_text = "Sign In" if self.mode == "signin" else "Create Account"
        btn_submit = QPushButton(btn_text)
        btn_submit.setFont(QFont("Arial", 15, QFont.Bold))
        btn_submit.setFixedSize(350, 50)
        btn_submit.setCursor(Qt.PointingHandCursor)
        btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        btn_submit.clicked.connect(self.handle_submit)
        layout.addWidget(btn_submit, alignment=Qt.AlignCenter)
        
        # Toggle link
        toggle_text = "Don't have an account? Sign Up" if self.mode == "signin" else "Already have an account? Sign In"
        btn_toggle = QPushButton(toggle_text)
        btn_toggle.setFont(QFont("Arial", 12))
        btn_toggle.setCursor(Qt.PointingHandCursor)
        btn_toggle.setStyleSheet("""
            QPushButton {
                color: #2E7D32;
                border: none;
                background: transparent;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #388E3C;
            }
        """)
        btn_toggle.clicked.connect(self.toggle_mode)
        layout.addWidget(btn_toggle, alignment=Qt.AlignCenter)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(layout)
        
        # Set background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#F5F5F5"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
    
    def handle_submit(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "Error", "Username must be at least 3 characters")
            return
        
        if len(password) < 4:
            QMessageBox.warning(self, "Error", "Password must be at least 4 characters")
            return
        
        if self.mode == "signup":
            confirm = self.confirm_input.text()
            if password != confirm:
                QMessageBox.warning(self, "Error", "Passwords don't match")
                return
            self.create_account(username, password)
        else:
            self.sign_in(username, password)
    
    def create_account(self, username, password):
        users = self.load_users()
        
        if username in users:
            QMessageBox.warning(self, "Error", "Username already exists")
            return
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        users[username] = {
            "password": password_hash,
            "created_at": datetime.now().isoformat()
        }
        self.save_users(users)
        
        # Create user session folder
        os.makedirs(os.path.join(DATA_DIR, "sessions", username), exist_ok=True)
        
        QMessageBox.information(self, "Success", f"Account created successfully!\n\nWelcome, {username}!")
        self.toggle_mode()
    
    def sign_in(self, username, password):
        users = self.load_users()
        
        if username not in users:
            QMessageBox.warning(self, "Error", "Username not found")
            return
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[username]["password"] != password_hash:
            QMessageBox.warning(self, "Error", "Incorrect password")
            return
        
        # Success!
        self.app.show_input_screen(username=username)
    
    def load_users(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(self.users_file):
            return {}
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users):
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def toggle_mode(self):
        new_mode = "signup" if self.mode == "signin" else "signin"
        self.app.show_auth_screen(mode=new_mode)
    
    def go_back(self):
        self.app.show_welcome_screen()
