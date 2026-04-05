from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
import requests
from utils.api_client import APIClient

class LoadingScreen(QWidget):
    def __init__(self, user_text, username, parent=None, game_data=None,
                 duration_seconds=None, face_image_b64=None, face_consent=False):
        super().__init__()
        self.app = parent
        self.user_text = user_text
        self.username = username
        self.game_data = game_data
        self.duration_seconds = duration_seconds if duration_seconds else 60
        self.duration_minutes = max(1, int(round(self.duration_seconds / 60)))
        self.face_image_b64 = face_image_b64
        self.face_consent = face_consent
        self.progress = 0
        self.api_client = APIClient()
        self.setup_ui()
        self.start_processing()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Loading animation
        title = QLabel("🧠 Analyzing...")
        title.setFont(QFont("Arial", 38, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E7D32;")
        layout.addWidget(title)
        
        # Subtitle with animation
        subtitle_text = "Understanding your gameplay patterns" if self.game_data is not None else "Understanding your feelings"
        self.subtitle = QLabel(subtitle_text)
        self.subtitle.setFont(QFont("Arial", 16))
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: #666;")
        layout.addWidget(self.subtitle)
        
        # Animated dots
        self.dot_count = 0
        self.dot_timer = QTimer()
        self.dot_timer.timeout.connect(self.animate_dots)
        self.dot_timer.start(500)
        
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(450, 35)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #DDD;
                border-radius: 8px;
                text-align: center;
                background-color: white;
                color: #333;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #2E7D32;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        
        # Status messages
        self.status_label = QLabel("Connecting to AI...")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(layout)
        
        # Background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#F5F5F5"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
    
    def animate_dots(self):
        dots = "." * (self.dot_count % 4)
        if self.game_data is not None:
            self.subtitle.setText(f"Understanding your gameplay patterns{dots}")
        else:
            self.subtitle.setText(f"Understanding your feelings{dots}")
        self.dot_count += 1
    
    def start_processing(self):
        # Animate progress bar
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)
        
        # Send request to backend
        QTimer.singleShot(500, self.send_to_backend)
    
    def update_progress(self):
        if self.progress < 85:
            self.progress += 2
            self.progress_bar.setValue(self.progress)
            
            # Update status messages
            if self.progress < 30:
                self.status_label.setText("Connecting to AI...")
            elif self.progress < 60:
                self.status_label.setText("Analyzing emotional content...")
            else:
                self.status_label.setText("Generating recommendations...")
    
    def send_to_backend(self):
        if self.game_data is not None:
            self.send_game_to_backend()
            return

        self.send_text_to_backend()

    def send_game_to_backend(self):
        try:
            print("[INFO] Sending gameplay metrics to backend...")

            result = self.api_client.analyze_game(
                self.username,
                self.game_data,
                self.duration_minutes
            )

            if not isinstance(result, dict) or 'metrics' not in result:
                detail = result.get('detail', 'Invalid game analysis response') if isinstance(result, dict) else 'Invalid game analysis response'
                self.show_error(str(detail))
                return

            print("\n" + "="*60)
            print("[FRONTEND] Game analysis response received!")
            print(f"[FRONTEND] Metrics: {result.get('metrics', {})}")
            print(f"[FRONTEND] Recommendations count: {len(result.get('recommendations', []))}")
            print(f"[FRONTEND] Source: {result.get('source', 'N/A')}")
            print("="*60 + "\n")

            self.finish_with_result(result)

        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def send_text_to_backend(self):
        try:
            print(f"[INFO] Sending to backend: {self.user_text[:50]}...")

            payload = {
                "user_input": self.user_text,
                "username": self.username,
                "face_consent": self.face_consent,
            }
            if self.face_consent and self.face_image_b64:
                payload["face_image_b64"] = self.face_image_b64
                print("[INFO] Face image included in request.")
            
            response = requests.post(
                "http://localhost:8000/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n" + "="*60)
                print("[FRONTEND] Analysis response received!")
                print(f"[FRONTEND] Metrics: {result.get('metrics', {})}")
                print(f"[FRONTEND] Recommendations count: {len(result.get('recommendations', []))}")
                if result.get('recommendations'):
                    for i, rec in enumerate(result['recommendations'], 1):
                        print(f"[FRONTEND]   {i}. {rec.get('name', 'Unknown')}")
                print(f"[FRONTEND] Visualization params: wellbeing={result.get('visualization', {}).get('wellbeing', 'N/A')}")
                print("="*60 + "\n")

                self.finish_with_result(result)
            else:
                self.show_error(f"Server error: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            self.show_error("Cannot connect to backend server.\n\nMake sure you started the backend:\npython backend/server.py")
        except requests.exceptions.Timeout:
            self.show_error("Request timed out. Please try again.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def finish_with_result(self, result):
        # Complete progress
        self.progress = 100
        self.progress_bar.setValue(100)
        self.status_label.setText("Analysis complete!")

        # Stop timers
        self.timer.stop()
        self.dot_timer.stop()

        # Show results after brief delay
        QTimer.singleShot(800, lambda: self.show_results(result))
    
    def show_results(self, result):
        self.app.show_result_screen(result, self.username)
    
    def show_error(self, error):
        self.timer.stop()
        self.dot_timer.stop()
        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", error)
        self.app.show_input_screen(self.username)
