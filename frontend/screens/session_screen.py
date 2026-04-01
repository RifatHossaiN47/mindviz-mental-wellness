from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QBrush, QPen
from opengl.exercise_widgets import get_exercise_widget
import requests
import math

class SessionScreen(QWidget):
    def __init__(self, technique, initial_metrics, username, parent=None):
        super().__init__()
        self.app = parent
        self.technique = technique
        self.initial_metrics = initial_metrics.copy()
        self.current_metrics = initial_metrics.copy()
        self.username = username
        self.setup_ui()
        self.start_session()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel(f"🧘 {self.technique['name']}")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setStyleSheet("color: #2E7D32;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        btn_exit = QPushButton("Exit Session")
        btn_exit.setFont(QFont("Arial", 11))
        btn_exit.setFixedSize(120, 35)
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        btn_exit.clicked.connect(self.exit_session)
        header_layout.addWidget(btn_exit)
        
        layout.addLayout(header_layout)
        
        # Progress bar
        self.progress_label = QLabel("Progress: 0:00 / 1:00")
        self.progress_label.setFont(QFont("Arial", 13))
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(22)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #DDD;
                border-radius: 8px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #2E7D32;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Exercise-specific visualization widget
        technique_id = self.technique.get('id', 'breathing_478')
        print(f"[SESSION] Loading exercise widget for: {technique_id}")
        self.exercise_widget = get_exercise_widget(technique_id)
        self.exercise_widget.setMinimumSize(500, 420)
        layout.addWidget(self.exercise_widget, alignment=Qt.AlignCenter)
        
        # Real-time metrics
        self.metrics_label = QLabel(self.get_metrics_text())
        self.metrics_label.setFont(QFont("Arial", 12))
        self.metrics_label.setStyleSheet("""
            background-color: #E8F5E9;
            padding: 12px;
            border-radius: 8px;
            color: #333;
        """)
        self.metrics_label.setWordWrap(True)
        layout.addWidget(self.metrics_label)
        
        self.setLayout(layout)
        
        # Background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#FAFAFA"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
    
    def start_session(self):
        # All sessions are 1 minute (60 seconds)
        self.session_duration = 60
        self.elapsed_time = 0
        
        # Timer for session progress
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session)
        self.session_timer.start(1000)  # Every second
        
        # Start exercise animation
        self.exercise_widget.start()
    
    def update_session(self):
        self.elapsed_time += 1
        
        # Update progress bar
        progress = int((self.elapsed_time / self.session_duration) * 100)
        self.progress_bar.setValue(min(progress, 100))
        
        mins = self.elapsed_time // 60
        secs = self.elapsed_time % 60
        self.progress_label.setText(f"Progress: {mins}:{secs:02d} / 1:00")
        
        # Simulate metric improvement (every 10 seconds)
        if self.elapsed_time % 10 == 0:
            self.improve_metrics()
        
        # Check if session complete
        if self.elapsed_time >= self.session_duration:
            self.complete_session()
    
    def improve_metrics(self):
        """Gradually improve metrics during session"""
        effects = self.technique['effects']
        
        # Apply small improvements over the 1-minute session
        # Total of ~6 updates (every 10s), so each applies 1/6 of total effect
        improvement_rate = 0.18
        
        for metric, effect in effects.items():
            if metric in self.current_metrics:
                change = effect * improvement_rate
                self.current_metrics[metric] = max(0.0, min(1.0, 
                    self.current_metrics[metric] + change))
        
        self.metrics_label.setText(self.get_metrics_text())
    
    def get_metrics_text(self):
        text = "📊 REAL-TIME FEEDBACK:\n"
        
        for metric in ['anxiety', 'mood', 'stress']:
            if metric in self.current_metrics:
                initial = int(self.initial_metrics[metric] * 100)
                current = int(self.current_metrics[metric] * 100)
                
                if current < initial:
                    arrow = "↓"
                    status = "improving"
                elif current > initial and metric == 'mood':
                    arrow = "↑"
                    status = "improving"
                else:
                    arrow = "→"
                    status = "stable"
                
                text += f"\n{metric.capitalize()}: {initial}% → {current}% {arrow} ({status})"
        
        return text
    
    def complete_session(self):
        self.session_timer.stop()
        self.exercise_widget.stop()
        
        # Save session to backend
        self.save_session()
        
        # Show completion message
        from PyQt5.QtWidgets import QMessageBox
        improvement_text = self.get_improvement_summary()
        QMessageBox.information(self, "Session Complete! 🎉", 
            f"Great work! You completed the {self.technique['name']} session.\n\n"
            f"{improvement_text}\n\n"
            "Keep practicing regularly for best results!")
        
        # Return to input screen
        self.app.show_input_screen(self.username)
    
    def get_improvement_summary(self):
        summary = []
        for metric in ['anxiety', 'mood', 'stress']:
            if metric in self.current_metrics:
                initial = self.initial_metrics[metric]
                final = self.current_metrics[metric]
                change = abs(final - initial)
                
                if change > 0.05:
                    if metric == 'mood':
                        if final > initial:
                            summary.append(f"✅ Mood improved by {int(change * 100)}%")
                    else:
                        if final < initial:
                            summary.append(f"✅ {metric.capitalize()} reduced by {int(change * 100)}%")
        
        return "\n".join(summary) if summary else "You completed the session!"
    
    def save_session(self):
        """Save session data to backend"""
        try:
            requests.post(
                "http://localhost:8000/save-session",
                json={
                    "username": self.username,
                    "initial_metrics": self.initial_metrics,
                    "final_metrics": self.current_metrics,
                    "technique": self.technique['id'],
                    "duration": 1  # 1 minute
                },
                timeout=5
            )
            print("[INFO] Session saved successfully")
        except Exception as e:
            print(f"[WARNING] Failed to save session: {e}")
    
    def exit_session(self):
        self.session_timer.stop()
        self.exercise_widget.stop()
        self.app.show_input_screen(self.username)
