import math
import random
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QTime, QRectF
from PyQt5.QtGui import (QPainter, QFont, QColor, QPen, QBrush,
                         QLinearGradient, QRadialGradient)


class GameScreen(QWidget):
    def __init__(self, app, username, duration_minutes):
        super().__init__()
        self.app = app

        self.username = username
        self.duration_seconds = duration_minutes * 60
        self.elapsed_seconds = 0
        self.bubbles = []
        self.reaction_times = []
        self.correct_pops = 0
        self.empty_clicks = 0
        self.total_clicks = 0
        self.pause_count = 0
        self.first_half_correct = 0
        self.second_half_correct = 0
        self.first_half_clicks = 0
        self.second_half_clicks = 0
        self.last_click_time = None
        self.spawn_timer_id = None
        self.game_finished = False
        self.score = 0

        self.pop_effects = []
        self.frame_time = 0.0

        self.setup_ui()
        self.start_game()

    def setup_ui(self):
        self.setMouseTracking(True)
        self.setAutoFillBackground(False)

        self.btn_exit = QPushButton("Exit Session", self)
        self.btn_exit.setFont(QFont("Arial", 11))
        self.btn_exit.setFixedSize(120, 35)
        self.btn_exit.setCursor(Qt.PointingHandCursor)
        self.btn_exit.setStyleSheet("""
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
        self.btn_exit.clicked.connect(self.exit_game)

    def resizeEvent(self, event):
        self.btn_exit.move(self.width() - 140, 20)
        super().resizeEvent(event)

    def start_game(self):
        # Main animation loop (~30fps)
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(33)

        # Game clock
        self.second_timer = QTimer()
        self.second_timer.timeout.connect(self.tick_second)
        self.second_timer.start(1000)

        # Bubble spawner
        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_bubbles)
        self.spawn_timer.start(random.randint(800, 1200))
        self.spawn_timer_id = self.spawn_timer

        # Spawn initial wave quickly
        QTimer.singleShot(220, self.spawn_bubbles)

    def stop_timers(self):
        for timer in [getattr(self, "game_timer", None),
                      getattr(self, "second_timer", None),
                      getattr(self, "spawn_timer", None)]:
            if timer:
                timer.stop()

    def tick_second(self):
        if self.game_finished:
            return

        self.elapsed_seconds += 1
        if self.elapsed_seconds >= self.duration_seconds:
            self.complete_game()
        self.update()

    def spawn_bubbles(self):
        if self.game_finished:
            return

        spawn_count = random.randint(1, 2)
        for _ in range(spawn_count):
            self.bubbles.append(self._create_bubble())

        self.spawn_timer.setInterval(random.randint(800, 1200))

    def _create_bubble(self):
        roll = random.random()
        if roll < 0.50:
            bubble_type = "calm"
            radius = random.uniform(35, 50)
            color = QColor(102, 187, 255, 215)
            speed_y = random.uniform(1.2, 1.8)
            lifetime_ms = 4000
        elif roll < 0.75:
            bubble_type = "stress"
            radius = random.uniform(20, 30)
            color = QColor(255, 112, 96, 225)
            speed_y = random.uniform(2.2, 3.1)
            lifetime_ms = 2500
        elif roll < 0.90:
            bubble_type = "joy"
            radius = random.uniform(12, 18)
            color = QColor(255, 214, 80, 235)
            speed_y = random.uniform(1.9, 2.7)
            lifetime_ms = 1500
        else:
            bubble_type = "decoy"
            radius = random.uniform(25, 40)
            color = QColor(70, 78, 95, 220)
            speed_y = random.uniform(1.1, 1.6)
            lifetime_ms = 3600

        padding = radius + 25
        width = max(self.width(), 900)
        x = random.uniform(padding, max(padding + 1, width - padding))
        y = self.height() - random.uniform(95, 140)

        return {
            "x": x,
            "y": y,
            "radius": radius,
            "color": color,
            "type": bubble_type,
            "spawn_time": QTime.currentTime().msecsSinceStartOfDay(),
            "speed_x": random.uniform(-0.35, 0.35),
            "speed_y": speed_y,
            "lifetime_ms": lifetime_ms,
            "pulse_phase": random.uniform(0, 6.28),
        }

    def update_game(self):
        if self.game_finished:
            return

        now_ms = QTime.currentTime().msecsSinceStartOfDay()
        self.frame_time += 0.033

        remaining = []
        for bubble in self.bubbles:
            bubble["y"] -= bubble["speed_y"]
            bubble["x"] += bubble["speed_x"]

            # Mild horizontal bounce at boundaries
            if bubble["x"] < bubble["radius"] + 10 or bubble["x"] > self.width() - bubble["radius"] - 10:
                bubble["speed_x"] *= -1

            age = now_ms - bubble["spawn_time"]
            if bubble["y"] < 80:
                continue
            if age > bubble["lifetime_ms"]:
                continue

            remaining.append(bubble)

        self.bubbles = remaining

        # Pop effect fade-out
        active_effects = []
        for effect in self.pop_effects:
            age = now_ms - effect["start_ms"]
            if age <= 300:
                effect["age"] = age
                active_effects.append(effect)
        self.pop_effects = active_effects

        self.update()

    def _is_second_half(self):
        return self.elapsed_seconds >= (self.duration_seconds / 2)

    def _register_half_click(self, is_correct):
        if self._is_second_half():
            self.second_half_clicks += 1
            if is_correct:
                self.second_half_correct += 1
        else:
            self.first_half_clicks += 1
            if is_correct:
                self.first_half_correct += 1

    def mousePressEvent(self, event):
        if self.game_finished:
            super().mousePressEvent(event)
            return

        if event.button() != Qt.LeftButton:
            super().mousePressEvent(event)
            return

        if self.btn_exit.geometry().contains(event.pos()):
            super().mousePressEvent(event)
            return

        self.total_clicks += 1

        now_ms = QTime.currentTime().msecsSinceStartOfDay()
        if self.last_click_time is not None and (now_ms - self.last_click_time) > 3000:
            self.pause_count += 1
        self.last_click_time = now_ms

        hit_index = -1
        hit_type = None

        for i in range(len(self.bubbles) - 1, -1, -1):
            bubble = self.bubbles[i]
            dx = event.x() - bubble["x"]
            dy = event.y() - bubble["y"]
            if math.sqrt((dx * dx) + (dy * dy)) <= bubble["radius"]:
                hit_index = i
                hit_type = bubble["type"]
                break

        if hit_index >= 0:
            bubble = self.bubbles.pop(hit_index)

            if hit_type != "decoy":
                reaction_time = now_ms - bubble["spawn_time"]
                self.reaction_times.append(float(reaction_time))
                self.correct_pops += 1
                self._register_half_click(is_correct=True)

                if hit_type == "calm":
                    self.score += 10
                elif hit_type == "stress":
                    self.score += 12
                else:
                    self.score += 16
            else:
                self.empty_clicks += 1
                self._register_half_click(is_correct=False)
                self.score = max(0, self.score - 5)

            self.pop_effects.append({
                "x": bubble["x"],
                "y": bubble["y"],
                "color": bubble["color"],
                "start_ms": now_ms,
                "age": 0,
            })
        else:
            self.empty_clicks += 1
            self._register_half_click(is_correct=False)
            self.score = max(0, self.score - 1)

        self.update()
        super().mousePressEvent(event)

    def _format_time(self, seconds):
        mins = max(0, seconds) // 60
        secs = max(0, seconds) % 60
        return f"{mins:02d}:{secs:02d}"

    def _draw_hud(self, painter):
        width = self.width()

        # Top HUD panel
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(8, 14, 28, 185))
        painter.drawRect(0, 0, width, 78)

        painter.setPen(QColor(225, 235, 255))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(24, 32, f"Score: {self.score}")
        painter.drawText(24, 56, f"Pops: {self.correct_pops}")

        time_left = self.duration_seconds - self.elapsed_seconds
        painter.setFont(QFont("Arial", 18, QFont.Bold))
        painter.setPen(QColor(150, 230, 180))
        painter.drawText(width // 2 - 48, 48, self._format_time(time_left))

        # Time progress bar (right)
        bar_x = width - 360
        bar_y = 28
        bar_w = 180
        bar_h = 16
        progress = self.elapsed_seconds / max(self.duration_seconds, 1)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(48, 56, 72))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 7, 7)

        painter.setBrush(QColor(46, 125, 50))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w * progress, bar_h), 7, 7)

        painter.setPen(QColor(185, 195, 220))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(bar_x - 78, bar_y + 13, "Progress")

    def _draw_bottom_hint(self, painter):
        w = self.width()
        h = self.height()

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(8, 14, 28, 170))
        painter.drawRect(0, h - 52, w, 52)

        painter.setPen(QColor(215, 225, 245))
        painter.setFont(QFont("Arial", 12))
        painter.drawText(20, h - 20, "Click the glowing bubbles! Avoid the dark ones.")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # Background gradient
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, QColor(8, 22, 44))
        bg.setColorAt(1, QColor(5, 12, 26))
        painter.fillRect(self.rect(), QBrush(bg))

        # Soft background glow
        ambient = QRadialGradient(w * 0.5, h * 0.72, max(w, h) * 0.75)
        ambient.setColorAt(0, QColor(25, 70, 95, 65))
        ambient.setColorAt(1, QColor(10, 16, 30, 0))
        painter.fillRect(self.rect(), QBrush(ambient))

        # Draw bubbles
        for bubble in self.bubbles:
            radius = bubble["radius"]
            if bubble["type"] == "joy":
                pulse = 1.0 + math.sin((self.frame_time * 6.5) + bubble["pulse_phase"]) * 0.14
                radius = bubble["radius"] * pulse

            cx = bubble["x"]
            cy = bubble["y"]
            color = bubble["color"]

            glow = QColor(color.red(), color.green(), color.blue(), 70)
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QRectF(cx - radius - 8, cy - radius - 8, (radius + 8) * 2, (radius + 8) * 2))

            painter.setBrush(color)
            painter.setPen(QPen(QColor(245, 250, 255, 200), 2))
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

            highlight = QColor(255, 255, 255, 95)
            painter.setPen(Qt.NoPen)
            painter.setBrush(highlight)
            painter.drawEllipse(QRectF(cx - radius * 0.45, cy - radius * 0.55, radius * 0.5, radius * 0.5))

            if bubble["type"] == "decoy":
                painter.setPen(QPen(QColor(25, 25, 35, 180), 2))
                painter.drawLine(int(cx - radius * 0.5), int(cy - radius * 0.5),
                                 int(cx + radius * 0.5), int(cy + radius * 0.5))
                painter.drawLine(int(cx + radius * 0.5), int(cy - radius * 0.5),
                                 int(cx - radius * 0.5), int(cy + radius * 0.5))

        # Draw pop effects
        for effect in self.pop_effects:
            progress = effect["age"] / 300.0
            pr = 8 + (progress * 26)
            alpha = int(180 * (1 - progress))
            col = effect["color"]
            ring_color = QColor(col.red(), col.green(), col.blue(), max(0, alpha))

            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(ring_color, 2))
            painter.drawEllipse(QRectF(effect["x"] - pr, effect["y"] - pr, pr * 2, pr * 2))

        self._draw_hud(painter)
        self._draw_bottom_hint(painter)

        painter.end()

    def complete_game(self):
        if self.game_finished:
            return

        self.game_finished = True
        self.stop_timers()

        first_half_accuracy = self.first_half_correct / max(self.first_half_clicks, 1)
        second_half_accuracy = self.second_half_correct / max(self.second_half_clicks, 1)
        accuracy_trend = second_half_accuracy - first_half_accuracy

        game_data = {
            "reaction_times": self.reaction_times,
            "correct_pops": self.correct_pops,
            "empty_clicks": self.empty_clicks,
            "total_clicks": self.total_clicks,
            "total_seconds": self.elapsed_seconds,
            "pause_count": self.pause_count,
            "accuracy_trend": accuracy_trend,
        }

        self.app.show_loading_screen_for_game(game_data, self.username, self.duration_seconds)

    def exit_game(self):
        self.game_finished = True
        self.stop_timers()
        self.app.show_input_screen(self.username)
