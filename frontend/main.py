from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
import sys
from screens.welcome_screen import WelcomeScreen
from screens.auth_screen import AuthScreen
from screens.input_screen import InputScreen
from screens.loading_screen import LoadingScreen
from screens.result_screen import ResultScreen
from screens.session_screen import SessionScreen
from screens.journey_screen import JourneyScreen
from screens.game_mode_screen import GameModeScreen
from screens.game_screen import GameScreen

class MindVizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MindViz - Mental Wellness Visualization")
        self.setGeometry(100, 50, 1400, 900)
        
        # Stack of screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Start with welcome screen
        self.show_welcome_screen()
    
    def clear_and_add(self, screen):
        """Clear old screens and add new one"""
        # Keep only last 3 screens in memory
        while self.stacked_widget.count() > 3:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        self.stacked_widget.addWidget(screen)
        self.stacked_widget.setCurrentWidget(screen)
    
    def show_welcome_screen(self):
        screen = WelcomeScreen(self)
        self.clear_and_add(screen)
    
    def show_auth_screen(self, mode="signin"):
        screen = AuthScreen(mode, self)
        self.clear_and_add(screen)
    
    def show_input_screen(self, username):
        screen = InputScreen(username, self)
        self.clear_and_add(screen)
    
    def show_loading_screen(self, text, username, face_image=None):
        screen = LoadingScreen(text, username, self, face_image=face_image)
        self.clear_and_add(screen)

    def show_loading_screen_for_game(self, game_data, username, duration_seconds):
        screen = LoadingScreen(
            "",
            username,
            self,
            game_data=game_data,
            duration_seconds=duration_seconds
        )
        self.clear_and_add(screen)
    
    def show_result_screen(self, result, username):
        screen = ResultScreen(result, username, self)
        self.clear_and_add(screen)
    
    def show_session_screen(self, technique, initial_metrics, username):
        screen = SessionScreen(technique, initial_metrics, username, self)
        self.clear_and_add(screen)
    
    def show_journey_screen(self, username):
        screen = JourneyScreen(username, self)
        self.clear_and_add(screen)

    def show_game_mode_screen(self, username):
        screen = GameModeScreen(username, self)
        self.clear_and_add(screen)

    def show_game_screen(self, username, duration_minutes):
        screen = GameScreen(self, username, duration_minutes)
        self.clear_and_add(screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = MindVizApp()
    window.show()
    
    print("=" * 60)
    print("🌱 MindViz Frontend Started")
    print("=" * 60)
    print("Make sure backend is running at http://localhost:8000")
    print("=" * 60)
    
    sys.exit(app.exec_())
