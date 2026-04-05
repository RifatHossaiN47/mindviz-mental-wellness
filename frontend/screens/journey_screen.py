from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from opengl.journey_renderer import JourneyWidget
import requests

class JourneyScreen(QWidget):
    def __init__(self, username, parent=None):
        super().__init__()
        self.app = parent
        self.username = username
        self.sessions = []
        self.selected_index = -1
        self.load_sessions()
        self.setup_ui()
    
    def load_sessions(self):
        """Load user's session history from backend"""
        try:
            response = requests.get(f"http://localhost:8000/get-sessions/{self.username}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                sessions = data.get('sessions', [])
                self.sessions = sorted(sessions, key=lambda item: item.get('date', ''))
                print(f"[INFO] Loaded {len(self.sessions)} sessions")
        except Exception as e:
            print(f"[ERROR] Failed to load sessions: {e}")
            self.sessions = []
    
    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # LEFT: 3D Journey visualization (70% width)
        if len(self.sessions) >= 2:
            try:
                self.journey_widget = JourneyWidget(self.sessions)
                self.journey_widget.point_clicked.connect(self.on_point_selected)
                self.journey_widget.point_hovered.connect(self.on_point_hovered)
                main_layout.addWidget(self.journey_widget, stretch=7)
            except Exception as e:
                print(f"[ERROR] Failed to create journey: {e}")
                placeholder = self.create_placeholder("3D Journey Map\n(Requires OpenGL)")
                main_layout.addWidget(placeholder, stretch=7)
        else:
            placeholder = self.create_placeholder(
                "Not enough data yet!\n\n"
                "Complete at least 2 sessions\n"
                "to see your journey."
            )
            main_layout.addWidget(placeholder, stretch=7)
        
        # RIGHT: Statistics panel (30% width)
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(25, 25, 25, 25)
        
        # Header
        header = QLabel("🗺️ YOUR WELLNESS JOURNEY")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2E7D32;")
        right_layout.addWidget(header)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #DDD;")
        right_layout.addWidget(line)
        
        # Statistics
        if self.sessions:
            stats_layout = QVBoxLayout()
            stats_layout.setSpacing(15)
            
            # Total sessions
            self.add_stat(stats_layout, "📊 Total Sessions", str(len(self.sessions)))
            
            # Calculate average improvement
            total_improvement = 0
            for session in self.sessions:
                imp = session.get('improvement', {})
                anxiety_imp = imp.get('anxiety', 0)
                stress_imp = imp.get('stress', 0)
                mood_imp = imp.get('mood', 0)
                total_improvement += (anxiety_imp + stress_imp + mood_imp) / 3
            
            avg_improvement = (total_improvement / len(self.sessions)) * 100 if self.sessions else 0
            
            self.add_stat(stats_layout, "📈 Avg Improvement", f"{int(avg_improvement)}%")
            
            # Most used technique
            techniques = {}
            for session in self.sessions:
                tech = session.get('technique', 'unknown')
                techniques[tech] = techniques.get(tech, 0) + 1
            
            if techniques:
                most_used = max(techniques, key=techniques.get)
                self.add_stat(stats_layout, "⭐ Favorite Technique", 
                            self.format_technique_name(most_used))
            
            # Current trend
            if len(self.sessions) >= 3:
                recent_sessions = self.sessions[-3:]
                trend = self.calculate_trend(recent_sessions)
                trend_emoji = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                trend_text = "Improving!" if trend > 0 else "Declining" if trend < 0 else "Stable"
                self.add_stat(stats_layout, f"{trend_emoji} Recent Trend", trend_text)
            
            right_layout.addLayout(stats_layout)
        else:
            no_data = QLabel("No session data yet.\n\nStart your first wellness session to track your progress!")
            no_data.setWordWrap(True)
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #999; font-size: 14px;")
            right_layout.addWidget(no_data)
        
        # Selected session detail panel
        self.detail_frame = QFrame()
        self.detail_frame.setVisible(False)
        self.detail_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F5E9;
                border: 2px solid #A5D6A7;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        det_layout = QVBoxLayout()
        det_layout.setSpacing(6)
        self.detail_title = QLabel("")
        self.detail_title.setFont(QFont("Arial", 10, QFont.Bold))
        self.detail_title.setStyleSheet("color: #2E7D32; border: none;")
        self.detail_title.setWordWrap(True)
        det_layout.addWidget(self.detail_title)
        self.detail_date = QLabel("")
        self.detail_date.setFont(QFont("Arial", 9))
        self.detail_date.setStyleSheet("color: #555; border: none;")
        det_layout.addWidget(self.detail_date)
        self.detail_metrics = QLabel("")
        self.detail_metrics.setFont(QFont("Arial", 9))
        self.detail_metrics.setStyleSheet("color: #333; border: none;")
        self.detail_metrics.setWordWrap(True)
        det_layout.addWidget(self.detail_metrics)
        self.detail_frame.setLayout(det_layout)
        right_layout.addWidget(self.detail_frame)
        
        # Journey explanation
        right_layout.addStretch()
        
        explanation = QLabel(
            "💡 About Your Journey:\n\n"
            "The 3D path shows your mental wellness over time. "
            "Each point represents a completed session.\n"
            "Hover any point to preview detailed metrics.\n"
            "Click a point to pin full details.\n\n"
            "🔴 Red: High stress\n"
            "🟠 Orange: Moderate\n"
            "🟡 Yellow: Good\n"
            "🟢 Green: Excellent\n\n"
            "Height shows overall wellbeing."
        )
        explanation.setWordWrap(True)
        explanation.setFont(QFont("Arial", 9))
        explanation.setStyleSheet("""
            background-color: #F5F5F5;
            padding: 15px;
            border-radius: 8px;
            color: #555;
        """)
        right_layout.addWidget(explanation)
        
        # Back button
        btn_back = QPushButton("← Back to Home")
        btn_back.setFont(QFont("Arial", 11, QFont.Bold))
        btn_back.setFixedHeight(45)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet("""
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
        btn_back.clicked.connect(self.go_back)
        right_layout.addWidget(btn_back)
        
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, stretch=3)
        
        self.setLayout(main_layout)
    
    def create_placeholder(self, text):
        widget = QLabel(text)
        widget.setAlignment(Qt.AlignCenter)
        widget.setFont(QFont("Arial", 14))
        widget.setStyleSheet("background-color: #E8F5E9; color: #555;")
        return widget
    
    def add_stat(self, layout, label, value):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #F9F9F9;
                border-left: 4px solid #2E7D32;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        stat_layout = QVBoxLayout()
        stat_layout.setSpacing(5)
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Arial", 9))
        label_widget.setStyleSheet("color: #666;")
        stat_layout.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Arial", 14, QFont.Bold))
        value_widget.setStyleSheet("color: #2E7D32;")
        stat_layout.addWidget(value_widget)
        
        container.setLayout(stat_layout)
        layout.addWidget(container)
    
    def format_technique_name(self, tech_id):
        names = {
            "breathing_478": "4-7-8 Breathing",
            "progressive_relaxation": "Progressive Relaxation",
            "cognitive_reframe": "Cognitive Reframing",
            "box_breathing": "Box Breathing",
            "grounding_54321": "5-4-3-2-1 Grounding",
            "body_scan": "Body Scan",
            "deep_breathing": "Deep Breathing",
            "mindful_walking": "Mindful Walking",
            "gratitude_practice": "Gratitude Practice",
            "visualization": "Visualization",
            "positive_affirmations": "Positive Affirmations",
            "journaling": "Journaling",
            "music_therapy": "Music Therapy",
            "physical_exercise": "Physical Exercise",
            "social_connection": "Social Connection",
            "sleep_hygiene": "Sleep Hygiene",
            "time_in_nature": "Nature Therapy",
            "digital_detox": "Digital Detox",
            "healthy_eating": "Healthy Eating",
            "stretching": "Stretching",
            "professional_support": "Professional Support"
        }
        return names.get(tech_id, tech_id.replace("_", " ").title())
    
    def calculate_trend(self, sessions):
        """Calculate if recent trend is improving or declining"""
        if len(sessions) < 2:
            return 0
        
        scores = []
        for session in sessions:
            final = session.get('final_metrics', {})
            # Higher is better: calculate overall wellbeing
            anxiety = final.get('anxiety', 0.5)
            mood = final.get('mood', 0.5)
            stress = final.get('stress', 0.5)
            wellbeing = (1 - anxiety + mood + (1 - stress)) / 3
            scores.append(wellbeing)
        
        # Simple linear trend
        return scores[-1] - scores[0]

    def _update_detail_panel(self, index, pinned=False):
        """Populate detail panel with richer journey insights for one session."""
        if index < 0 or index >= len(self.sessions):
            self.detail_frame.setVisible(False)
            return

        session = self.sessions[index]
        initial = session.get('initial_metrics', {})
        final = session.get('final_metrics', {})
        improvement = session.get('improvement', {})
        tech_id = session.get('technique', 'unknown')
        tech = self.format_technique_name(tech_id)
        date = session.get('date', '')[:16].replace('T', ' ')

        duration = session.get('duration', 1)
        if not isinstance(duration, (int, float)):
            duration = 1
        duration = int(max(1, duration))

        tech_count = sum(1 for s in self.sessions if s.get('technique') == tech_id)

        anx_b = int(initial.get('anxiety', 0.5) * 100)
        anx_a = int(final.get('anxiety', 0.5) * 100)
        mood_b = int(initial.get('mood', 0.5) * 100)
        mood_a = int(final.get('mood', 0.5) * 100)
        str_b = int(initial.get('stress', 0.5) * 100)
        str_a = int(final.get('stress', 0.5) * 100)

        anx_arrow = "\u2193" if anx_a < anx_b else "\u2191" if anx_a > anx_b else "\u2192"
        mood_arrow = "\u2191" if mood_a > mood_b else "\u2193" if mood_a < mood_b else "\u2192"
        str_arrow = "\u2193" if str_a < str_b else "\u2191" if str_a > str_b else "\u2192"

        wellbeing_before = int(((1 - initial.get('anxiety', 0.5))
                                + initial.get('mood', 0.5)
                                + (1 - initial.get('stress', 0.5))) / 3 * 100)
        wellbeing_after = int(((1 - final.get('anxiety', 0.5))
                               + final.get('mood', 0.5)
                               + (1 - final.get('stress', 0.5))) / 3 * 100)
        wellbeing_change = wellbeing_after - wellbeing_before
        wb_sign = "+" if wellbeing_change > 0 else ""

        improvement_candidates = [
            ("Anxiety", improvement.get('anxiety', 0)),
            ("Mood", improvement.get('mood', 0)),
            ("Stress", improvement.get('stress', 0)),
        ]
        best_metric, best_val = max(improvement_candidates, key=lambda item: item[1])
        if best_val > 0.01:
            insight = f"Best gain: {best_metric} improved {int(best_val * 100)}%"
        elif best_val < -0.01:
            insight = f"Watch point: {best_metric} dropped {int(abs(best_val) * 100)}%"
        else:
            insight = "Balanced session with steady metrics"

        title_prefix = "Pinned" if pinned else "Hover"
        self.detail_title.setText(f"{title_prefix} Session {index + 1}: {tech}")
        self.detail_date.setText(f"Date: {date}")
        self.detail_metrics.setText(
            f"Anxiety:  {anx_b}% {anx_arrow} {anx_a}%\n"
            f"Mood:     {mood_b}% {mood_arrow} {mood_a}%\n"
            f"Stress:   {str_b}% {str_arrow} {str_a}%\n"
            f"Wellbeing: {wellbeing_before}% -> {wellbeing_after}% ({wb_sign}{wellbeing_change}%)\n"
            f"Technique usage: {tech_count}x   Duration: {duration} min\n"
            f"{insight}"
        )
        self.detail_frame.setVisible(True)
    
    def on_point_selected(self, index):
        """Update detail panel when a journey point is clicked"""
        self.selected_index = index
        if index < 0 or index >= len(self.sessions):
            self.detail_frame.setVisible(False)
            return

        self._update_detail_panel(index, pinned=True)

    def on_point_hovered(self, index):
        """Show quick detail updates while hovering when nothing is pinned."""
        if self.selected_index >= 0:
            return

        if index < 0 or index >= len(self.sessions):
            self.detail_frame.setVisible(False)
            return

        self._update_detail_panel(index, pinned=False)
    
    def go_back(self):
        self.app.show_input_screen(self.username)
