from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from opengl.garden_renderer import GardenWidget

class ResultScreen(QWidget):
    def __init__(self, result_data, username, parent=None):
        super().__init__()
        self.app = parent
        self.result = result_data
        self.username = username
        
        print("\n" + "="*60)
        print("[RESULT SCREEN] Initializing...")
        print(f"[RESULT SCREEN] Metrics: {self.result.get('metrics', {})}")
        print(f"[RESULT SCREEN] Recommendations: {len(self.result.get('recommendations', []))} items")
        print(f"[RESULT SCREEN] Visualization: {list(self.result.get('visualization', {}).keys())}")
        print("="*60 + "\n")
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # LEFT SIDE: OpenGL Garden (55% width)
        try:
            self.garden = GardenWidget(self.result['visualization'], metrics=self.result.get('metrics', {}))
            main_layout.addWidget(self.garden, stretch=55)
        except Exception as e:
            print(f"[ERROR] Failed to create garden: {e}")
            placeholder = QLabel("Garden visualization\nrequires OpenGL")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("background-color: #E8F5E9; font-size: 18px;")
            main_layout.addWidget(placeholder, stretch=55)
        
        # RIGHT SIDE: Analysis, Metrics & Recommendations (45% width)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("border: none; background-color: white;")
        
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(22, 20, 22, 20)

        is_game_source = self.result.get("source") == "game"

        # Title row
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title_text = "🎮 Game Behavioral Analysis" if is_game_source else "🌱 YOUR MENTAL STATE"
        title = QLabel(title_text)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2E7D32;")
        title_row.addWidget(title)

        if is_game_source:
            game_badge = QLabel("Based on gameplay patterns")
            game_badge.setFont(QFont("Arial", 10, QFont.Bold))
            game_badge.setStyleSheet("""
                background-color: #E3F2FD;
                border: 1px solid #90CAF9;
                border-radius: 12px;
                padding: 6px 10px;
                color: #1565C0;
            """)
            game_badge.setAlignment(Qt.AlignCenter)
            title_row.addWidget(game_badge)

        title_row.addStretch()
        right_layout.addLayout(title_row)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #DDD;")
        right_layout.addWidget(line)
        
        # --- Gemini Analysis Text Section ---
        analysis = self.result.get('metrics', {}).get('analysis', {})
        
        if analysis and analysis.get('summary'):
            # Primary emotion badge
            primary = analysis.get('primary_emotion', '')
            if primary:
                emotion_badge = QLabel(f"🎭  Primary Emotion:  {primary}")
                emotion_badge.setFont(QFont("Arial", 12, QFont.Bold))
                emotion_badge.setStyleSheet("""
                    background-color: #E3F2FD;
                    border: 1px solid #90CAF9;
                    border-radius: 15px;
                    padding: 8px 14px;
                    color: #1565C0;
                """)
                emotion_badge.setAlignment(Qt.AlignCenter)
                right_layout.addWidget(emotion_badge)
            
            # Summary card
            summary_text = analysis.get('summary', '')
            if summary_text:
                summary_card = QLabel(f"📝  {summary_text}")
                summary_card.setWordWrap(True)
                summary_card.setFont(QFont("Arial", 11))
                summary_card.setStyleSheet("""
                    background-color: #F1F8E9;
                    border-left: 4px solid #7CB342;
                    padding: 12px;
                    border-radius: 4px;
                    color: #33691E;
                    line-height: 1.5;
                """)
                right_layout.addWidget(summary_card)
            
            # Mental state
            mental_state = analysis.get('mental_state', '')
            if mental_state:
                state_card = QLabel(f"🧠  Mental State:\n{mental_state}")
                state_card.setWordWrap(True)
                state_card.setFont(QFont("Arial", 10))
                state_card.setStyleSheet("""
                    background-color: #F3E5F5;
                    border-left: 4px solid #AB47BC;
                    padding: 10px;
                    border-radius: 4px;
                    color: #4A148C;
                """)
                right_layout.addWidget(state_card)
            
            # Emotional details
            emotional_details = analysis.get('emotional_details', [])
            if emotional_details:
                details_text = "\n".join([f"  •  {d}" for d in emotional_details])
                details_card = QLabel(f"💭  Emotional Details:\n{details_text}")
                details_card.setWordWrap(True)
                details_card.setFont(QFont("Arial", 10))
                details_card.setStyleSheet("""
                    background-color: #FFF3E0;
                    border-left: 4px solid #FF9800;
                    padding: 10px;
                    border-radius: 4px;
                    color: #E65100;
                """)
                right_layout.addWidget(details_card)
            
            # Body connection
            body = analysis.get('body_connection', '')
            if body:
                body_card = QLabel(f"🫀  Body Connection:\n{body}")
                body_card.setWordWrap(True)
                body_card.setFont(QFont("Arial", 10))
                body_card.setStyleSheet("""
                    background-color: #E8F5E9;
                    border-left: 4px solid #66BB6A;
                    padding: 10px;
                    border-radius: 4px;
                    color: #1B5E20;
                """)
                right_layout.addWidget(body_card)
            
            # Strength noted
            strength = analysis.get('strength_noted', '')
            if strength:
                strength_card = QLabel(f"💪  Strength Noted:\n{strength}")
                strength_card.setWordWrap(True)
                strength_card.setFont(QFont("Arial", 10))
                strength_card.setStyleSheet("""
                    background-color: #E0F7FA;
                    border-left: 4px solid #26C6DA;
                    padding: 10px;
                    border-radius: 4px;
                    color: #006064;
                """)
                right_layout.addWidget(strength_card)
            
            # Garden description
            garden_desc = analysis.get('garden_description', '')
            if garden_desc:
                garden_card = QLabel(f"🌿  Your Garden Reflects:\n{garden_desc}")
                garden_card.setWordWrap(True)
                garden_card.setFont(QFont("Arial", 10))
                garden_card.setStyleSheet("""
                    background-color: #F1F8E9;
                    border-left: 4px solid #9CCC65;
                    padding: 10px;
                    border-radius: 4px;
                    color: #33691E;
                """)
                right_layout.addWidget(garden_card)
        
        # Divider before metrics 
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("background-color: #DDD;")
        right_layout.addWidget(line2)
        
        # Metrics section
        metrics_label = QLabel("📊 EMOTIONAL METRICS")
        metrics_label.setFont(QFont("Arial", 13, QFont.Bold))
        metrics_label.setStyleSheet("color: #333;")
        right_layout.addWidget(metrics_label)
        
        metrics = self.result['metrics']
        self.add_metric(right_layout, "Anxiety", metrics['anxiety'])
        self.add_metric(right_layout, "Mood", metrics['mood'])
        self.add_metric(right_layout, "Stress", metrics['stress'])
        
        # Explanation box (Gemini-powered or fallback)
        if analysis and analysis.get('summary'):
            explanation_text = analysis.get('summary', self.get_explanation())
        else:
            explanation_text = self.get_explanation()
        
        explanation = QLabel(f"💡 {explanation_text}")
        explanation.setWordWrap(True)
        explanation.setFont(QFont("Arial", 10))
        explanation.setStyleSheet("""
            background-color: #FFF9E6;
            border-left: 4px solid #FFC107;
            padding: 10px;
            border-radius: 5px;
            color: #555;
        """)
        right_layout.addWidget(explanation)
        
        # Recommendations section
        right_layout.addSpacing(5)
        rec_label = QLabel("💊 RECOMMENDED FOR YOU")
        rec_label.setFont(QFont("Arial", 13, QFont.Bold))
        rec_label.setStyleSheet("color: #333;")
        right_layout.addWidget(rec_label)
        
        recommendations = self.result.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                self.add_recommendation(right_layout, rec)
        else:
            no_rec_label = QLabel("No recommendations available.\nPlease try analyzing again.")
            no_rec_label.setAlignment(Qt.AlignCenter)
            no_rec_label.setStyleSheet("color: #999; font-size: 12px; padding: 20px;")
            right_layout.addWidget(no_rec_label)
        
        # Bottom buttons
        right_layout.addSpacing(10)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_new = QPushButton("New Assessment")
        btn_new.setFont(QFont("Arial", 11))
        btn_new.setFixedHeight(40)
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        btn_new.clicked.connect(self.new_assessment)
        btn_layout.addWidget(btn_new)
        
        btn_journey = QPushButton("View Journey")
        btn_journey.setFont(QFont("Arial", 11))
        btn_journey.setFixedHeight(40)
        btn_journey.setCursor(Qt.PointingHandCursor)
        btn_journey.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2E7D32;
                border: 2px solid #2E7D32;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
        """)
        btn_journey.clicked.connect(self.view_journey)
        btn_layout.addWidget(btn_journey)
        
        right_layout.addLayout(btn_layout)
        
        right_widget.setLayout(right_layout)
        right_scroll.setWidget(right_widget)
        main_layout.addWidget(right_scroll, stretch=45)
        
        self.setLayout(main_layout)
    
    def add_metric(self, layout, name, value):
        container = QWidget()
        metric_layout = QVBoxLayout()
        metric_layout.setSpacing(4)
        metric_layout.setContentsMargins(0, 3, 0, 3)
        
        # Label with value and severity descriptor
        severity = self._get_severity(value, name)
        label = QLabel(f"{name}: {int(value * 100)}%  ({severity})")
        label.setFont(QFont("Arial", 11, QFont.Bold))
        label.setStyleSheet("color: #333;")
        metric_layout.addWidget(label)
        
        # Progress bar
        bar = QProgressBar()
        bar.setValue(int(value * 100))
        bar.setTextVisible(False)
        bar.setFixedHeight(18)
        bar.setStyleSheet(self.get_bar_style(value, name))
        metric_layout.addWidget(bar)
        
        container.setLayout(metric_layout)
        layout.addWidget(container)
    
    def _get_severity(self, value, name):
        if name == "Mood":
            if value > 0.75: return "Very Positive"
            if value > 0.6: return "Positive"
            if value > 0.45: return "Neutral"
            if value > 0.3: return "Low"
            return "Very Low"
        else:
            if value > 0.75: return "Severe"
            if value > 0.6: return "High"
            if value > 0.45: return "Moderate"
            if value > 0.3: return "Mild"
            return "Minimal"
    
    def get_bar_style(self, value, name):
        # For mood, higher is better
        if name == "Mood":
            if value > 0.7:
                color = "#4CAF50"  # Green - good
            elif value > 0.4:
                color = "#FF9800"  # Orange - okay
            else:
                color = "#F44336"  # Red - low
        else:
            # For anxiety/stress, lower is better
            if value > 0.7:
                color = "#F44336"  # Red - high
            elif value > 0.4:
                color = "#FF9800"  # Orange - moderate
            else:
                color = "#4CAF50"  # Green - low
        
        return f"""
            QProgressBar {{
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                background-color: #F5F5F5;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """
    
    def get_explanation(self):
        anxiety = self.result['metrics']['anxiety']
        mood = self.result['metrics']['mood']
        stress = self.result['metrics']['stress']
        
        if anxiety > 0.6 or stress > 0.6:
            return "Your anxiety or stress levels are elevated. The garden visualization shows darker skies and weather patterns reflecting these feelings. Try the recommended techniques to find relief."
        elif mood < 0.4:
            return "Your mood appears lower than usual. The garden reflects this with muted colors and drooping flowers. Engaging in the suggested activities may help lift your spirits."
        else:
            return "You're managing reasonably well! The garden shows a relatively calm state. Keep practicing wellness techniques to maintain balance."
    
    def add_recommendation(self, layout, rec):
        rec_widget = QFrame()
        rec_widget.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 5px;
            }
            QFrame:hover {
                border-color: #2E7D32;
                background-color: #F1F8F4;
            }
        """)
        
        rec_layout = QVBoxLayout()
        rec_layout.setSpacing(6)
        rec_layout.setContentsMargins(12, 10, 12, 10)
        
        # Technique name
        name = QLabel(f"🌬️ {rec['name']}")
        name.setFont(QFont("Arial", 12, QFont.Bold))
        name.setStyleSheet("color: #333;")
        rec_layout.addWidget(name)
        
        # Duration
        duration = QLabel(f"⏱️ Duration: {rec['duration']} minutes")
        duration.setFont(QFont("Arial", 10))
        duration.setStyleSheet("color: #666;")
        rec_layout.addWidget(duration)
        
        # Effects
        effects_text = self.format_effects(rec['effects'])
        effects = QLabel(f"✨ Effects: {effects_text}")
        effects.setFont(QFont("Arial", 10))
        effects.setStyleSheet("color: #555;")
        effects.setWordWrap(True)
        rec_layout.addWidget(effects)
        
        # Start button
        btn = QPushButton("START NOW")
        btn.setFont(QFont("Arial", 11, QFont.Bold))
        btn.setFixedHeight(35)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn.clicked.connect(lambda: self.start_session(rec))
        rec_layout.addWidget(btn)
        
        rec_widget.setLayout(rec_layout)
        layout.addWidget(rec_widget)
    
    def format_effects(self, effects):
        parts = []
        for key, value in effects.items():
            sign = "+" if value > 0 else ""
            parts.append(f"{sign}{int(value * 100)}% {key}")
        return ", ".join(parts)
    
    def start_session(self, technique):
        self.app.show_session_screen(technique, self.result['metrics'], self.username)
    
    def new_assessment(self):
        self.app.show_input_screen(self.username)
    
    def view_journey(self):
        self.app.show_journey_screen(self.username)
