from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class WelcomeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.app = parent
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Add top spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Logo/Title
        title = QLabel("🌱 MindViz")
        title.setFont(QFont("Arial", 58, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E7D32;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Mental Wellness Visualization")
        subtitle.setFont(QFont("Arial", 20))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #555;")
        layout.addWidget(subtitle)
        
        # Description
        desc = QLabel(
            "Transform your mental state into beautiful visualizations\n"
            "and practice evidence-based wellness techniques"
        )
        desc.setFont(QFont("Arial", 13))
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #777; margin: 20px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Add spacer
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Sign In Button
        btn_signin = QPushButton("Sign In")
        btn_signin.setFont(QFont("Arial", 15, QFont.Bold))
        btn_signin.setFixedSize(280, 55)
        btn_signin.setCursor(Qt.PointingHandCursor)
        btn_signin.setStyleSheet("""
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
        btn_signin.clicked.connect(self.show_signin)
        layout.addWidget(btn_signin, alignment=Qt.AlignCenter)
        
        # Sign Up Button
        btn_signup = QPushButton("Create Account")
        btn_signup.setFont(QFont("Arial", 15))
        btn_signup.setFixedSize(280, 55)
        btn_signup.setCursor(Qt.PointingHandCursor)
        btn_signup.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2E7D32;
                border-radius: 8px;
                border: 2px solid #2E7D32;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
        """)
        btn_signup.clicked.connect(self.show_signup)
        layout.addWidget(btn_signup, alignment=Qt.AlignCenter)
        
        # Guest Mode Button
        btn_guest = QPushButton("Continue as Guest")
        btn_guest.setFont(QFont("Arial", 12))
        btn_guest.setCursor(Qt.PointingHandCursor)
        btn_guest.setStyleSheet("""
            QPushButton {
                color: #777;
                border: none;
                background: transparent;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2E7D32;
            }
        """)
        btn_guest.clicked.connect(self.continue_guest)
        layout.addWidget(btn_guest, alignment=Qt.AlignCenter)

        # Divider
        divider = QLabel("— or —")
        divider.setFont(QFont("Arial", 11))
        divider.setAlignment(Qt.AlignCenter)
        divider.setStyleSheet("color: #AAA;")
        layout.addWidget(divider)

        # Game mode button
        btn_game = QPushButton("🎮 Play a Game Instead")
        btn_game.setFont(QFont("Arial", 13, QFont.Bold))
        btn_game.setFixedSize(280, 48)
        btn_game.setCursor(Qt.PointingHandCursor)
        btn_game.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2E7D32;
                border-radius: 8px;
                border: 2px solid #2E7D32;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
        """)
        btn_game.clicked.connect(self.show_game_mode)
        layout.addWidget(btn_game, alignment=Qt.AlignCenter)
        
        # Add spacer before developers section
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Developers section
        developers_title = QLabel("Developed by")
        developers_title.setFont(QFont("Arial", 10))
        developers_title.setAlignment(Qt.AlignCenter)
        developers_title.setStyleSheet("color: #999; margin-top: 10px;")
        layout.addWidget(developers_title)
        
        developers_names = QLabel(
            "Denesh Pantho Barua (ID: 2004101)\n"
            "Rifat Hossain (ID: 2004129)\n"
            "Nino Chakma (ID: 2004132)"
        )
        developers_names.setFont(QFont("Arial", 9))
        developers_names.setAlignment(Qt.AlignCenter)
        developers_names.setStyleSheet("color: #666; line-height: 1.4;")
        layout.addWidget(developers_names)
        
        # Add bottom spacer
        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(layout)
        
        # Set background color
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#F5F5F5"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
    
    def show_signin(self):
        self.app.show_auth_screen(mode="signin")
    
    def show_signup(self):
        self.app.show_auth_screen(mode="signup")
    
    def continue_guest(self):
        self.app.show_input_screen(username="Guest")

    def show_game_mode(self):
        self.app.show_game_mode_screen("Guest")
