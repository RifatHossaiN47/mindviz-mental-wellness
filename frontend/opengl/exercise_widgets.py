"""
20 Unique Exercise Visualization Widgets for MindViz
Each widget provides a custom animated visual guide for its specific technique.
All sessions are designed for 1 minute (60 seconds).
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import (QFont, QPainter, QColor, QBrush, QPen, QLinearGradient,
                         QRadialGradient, QPainterPath, QConicalGradient)
import math
import random


# ============================================================
# BASE CLASS
# ============================================================
class BaseExerciseWidget(QWidget):
    """Base class for all exercise visualization widgets."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.time = 0.0          # elapsed time in seconds
        self.phase_text = ""     # current instruction text
        self.sub_text = ""       # sub instruction
        self.setMinimumSize(500, 500)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._tick)
    
    def start(self):
        self.time = 0.0
        self.animation_timer.start(33)  # ~30 FPS
    
    def stop(self):
        self.animation_timer.stop()
    
    def _tick(self):
        self.time += 0.033
        self.update_state()
        self.update()
    
    def update_state(self):
        """Override in subclass to update animation state."""
        pass
    
    def draw_centered_text(self, painter, text, y_offset=0, size=28, color=QColor(255,255,255)):
        painter.setPen(QPen(color))
        painter.setFont(QFont("Arial", size, QFont.Bold))
        rect = self.rect()
        rect.moveTop(rect.top() + y_offset)
        painter.drawText(rect, Qt.AlignHCenter | Qt.AlignVCenter, text)
    
    def draw_text_at(self, painter, text, x, y, size=14, color=QColor(255,255,255), bold=False):
        painter.setPen(QPen(color))
        weight = QFont.Bold if bold else QFont.Normal
        painter.setFont(QFont("Arial", size, weight))
        painter.drawText(int(x), int(y), text)
    
    def draw_sub_text(self, painter, text, y_offset=60, size=16, color=QColor(220,220,220)):
        painter.setPen(QPen(color))
        painter.setFont(QFont("Arial", size))
        rect = self.rect()
        rect.moveTop(rect.top() + y_offset)
        painter.drawText(rect, Qt.AlignHCenter | Qt.AlignVCenter, text)


# ============================================================
# 1. BREATHING 4-7-8 WIDGET
# ============================================================
class Breathing478Widget(BaseExerciseWidget):
    """4-7-8 Breathing: Inhale 4s, Hold 7s, Exhale 8s. Cycle = 19s. ~3 cycles in 60s."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.radius = 60
        self.target_radius = 60
        self.cycle_time = 19  # 4+7+8
        self.phase = "INHALE"
        self.phase_progress = 0.0
        self.count = 0
    
    def update_state(self):
        t = self.time % self.cycle_time
        if t < 4:
            self.phase = "INHALE"
            self.phase_progress = t / 4.0
            self.count = int(t) + 1
            self.radius = 60 + self.phase_progress * 90
            self.phase_text = "INHALE"
            self.sub_text = f"Breathe in through nose... {self.count}"
        elif t < 11:
            self.phase = "HOLD"
            self.phase_progress = (t - 4) / 7.0
            self.count = int(t - 4) + 1
            self.radius = 150
            self.phase_text = "HOLD"
            self.sub_text = f"Hold your breath... {self.count}"
        else:
            self.phase = "EXHALE"
            self.phase_progress = (t - 11) / 8.0
            self.count = int(t - 11) + 1
            self.radius = 150 - self.phase_progress * 90
            self.phase_text = "EXHALE"
            self.sub_text = f"Breathe out through mouth... {self.count}"
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background gradient
        grad = QRadialGradient(cx, cy, max(w, h))
        grad.setColorAt(0, QColor(20, 30, 60))
        grad.setColorAt(1, QColor(5, 10, 30))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Glow rings
        if self.phase == "INHALE":
            base = QColor(33, 150, 243)
        elif self.phase == "HOLD":
            base = QColor(156, 39, 176)
        else:
            base = QColor(76, 175, 80)
        
        for i in range(5):
            alpha = 40 - i * 8
            glow = QColor(base.red(), base.green(), base.blue(), max(alpha, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            r = self.radius + i * 12
            painter.drawEllipse(QPointF(cx, cy), r, r)
        
        # Main circle
        painter.setBrush(QBrush(base))
        painter.setPen(QPen(base.darker(120), 3))
        painter.drawEllipse(QPointF(cx, cy), self.radius, self.radius)
        
        # Phase text
        self.draw_centered_text(painter, self.phase_text, -20, 30)
        
        # Count
        self.draw_centered_text(painter, str(self.count), 30, 22)
        
        # Sub text at bottom
        self.draw_sub_text(painter, self.sub_text, h // 2 - 60, 14, QColor(200, 200, 200))
        
        # Timing label
        self.draw_text_at(painter, "4-7-8 Breathing", 20, 30, 12, QColor(150, 150, 150))
        
        cycle_num = int(self.time // self.cycle_time) + 1
        self.draw_text_at(painter, f"Cycle {cycle_num}", 20, 50, 11, QColor(120, 120, 120))
        painter.end()


# ============================================================
# 2. PROGRESSIVE MUSCLE RELAXATION WIDGET
# ============================================================
class ProgressiveRelaxationWidget(BaseExerciseWidget):
    """Shows a body outline with muscle groups highlighting tense/relax phases."""
    MUSCLE_GROUPS = [
        ("Feet & Calves", 0.88),
        ("Thighs", 0.75),
        ("Hips & Buttocks", 0.65),
        ("Stomach", 0.55),
        ("Chest", 0.45),
        ("Hands & Arms", 0.50),
        ("Shoulders", 0.35),
        ("Neck", 0.28),
        ("Face", 0.18),
        ("Full Body", 0.50),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_group = 0
        self.is_tensing = True
    
    def update_state(self):
        # 6s per group: 3s tense + 3s relax = 6s * 10 groups = 60s
        group_duration = 6.0
        tense_duration = 3.0
        
        self.current_group = min(int(self.time // group_duration), len(self.MUSCLE_GROUPS) - 1)
        phase_time = self.time % group_duration
        self.is_tensing = phase_time < tense_duration
        self.phase_progress = phase_time / tense_duration if self.is_tensing else (phase_time - tense_duration) / (group_duration - tense_duration)
        
        name = self.MUSCLE_GROUPS[self.current_group][0]
        if self.is_tensing:
            self.phase_text = f"TENSE: {name}"
            self.sub_text = "Squeeze the muscles tightly..."
        else:
            self.phase_text = f"RELAX: {name}"
            self.sub_text = "Let go... feel the tension release..."
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(15, 25, 50))
        grad.setColorAt(1, QColor(30, 15, 40))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Draw body outline
        body_x = cx
        body_top = h * 0.08
        body_height = h * 0.80
        
        # Head
        head_r = body_height * 0.07
        head_cy = body_top + head_r
        painter.setPen(QPen(QColor(100, 150, 200), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(body_x, head_cy), head_r, head_r * 1.1)
        
        # Torso
        shoulder_y = head_cy + head_r * 1.3
        hip_y = body_top + body_height * 0.58
        shoulder_w = body_height * 0.15
        hip_w = body_height * 0.10
        
        painter.drawLine(int(body_x - shoulder_w), int(shoulder_y), int(body_x + shoulder_w), int(shoulder_y))
        painter.drawLine(int(body_x - shoulder_w), int(shoulder_y), int(body_x - hip_w), int(hip_y))
        painter.drawLine(int(body_x + shoulder_w), int(shoulder_y), int(body_x + hip_w), int(hip_y))
        painter.drawLine(int(body_x - hip_w), int(hip_y), int(body_x + hip_w), int(hip_y))
        
        # Arms
        arm_end_y = body_top + body_height * 0.55
        painter.drawLine(int(body_x - shoulder_w), int(shoulder_y), int(body_x - shoulder_w * 1.8), int(arm_end_y))
        painter.drawLine(int(body_x + shoulder_w), int(shoulder_y), int(body_x + shoulder_w * 1.8), int(arm_end_y))
        
        # Legs
        leg_end_y = body_top + body_height
        painter.drawLine(int(body_x - hip_w), int(hip_y), int(body_x - hip_w * 1.5), int(leg_end_y))
        painter.drawLine(int(body_x + hip_w), int(hip_y), int(body_x + hip_w * 1.5), int(leg_end_y))
        
        # Highlight current muscle group
        _, y_ratio = self.MUSCLE_GROUPS[self.current_group]
        highlight_y = body_top + body_height * y_ratio
        highlight_r = body_height * 0.08
        
        if self.is_tensing:
            pulse = 0.7 + 0.3 * math.sin(self.time * 6)
            color = QColor(255, 80, 80, int(180 * pulse))
        else:
            pulse = 0.5 + 0.5 * self.phase_progress
            color = QColor(80, 200, 120, int(150 * (1 - self.phase_progress * 0.5)))
        
        glow_grad = QRadialGradient(body_x, highlight_y, highlight_r * 2)
        glow_grad.setColorAt(0, color)
        glow_grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setBrush(QBrush(glow_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(body_x, highlight_y), highlight_r * 2, highlight_r * 1.5)
        
        # Phase text
        self.draw_centered_text(painter, self.phase_text, -h // 2 + 40, 22, QColor(255, 255, 255))
        self.draw_sub_text(painter, self.sub_text, h // 2 - 80, 14, QColor(180, 180, 180))
        
        # Group progress bar
        bar_w = w * 0.6
        bar_h = 8
        bar_x = (w - bar_w) / 2
        bar_y = h - 40
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(50, 50, 70)))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 4, 4)
        progress = (self.current_group + (self.time % 6) / 6) / len(self.MUSCLE_GROUPS)
        painter.setBrush(QBrush(QColor(100, 200, 150)))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w * progress, bar_h), 4, 4)
        
        self.draw_text_at(painter, f"Group {self.current_group + 1}/{len(self.MUSCLE_GROUPS)}", 20, 30, 11, QColor(120, 120, 120))
        painter.end()


# ============================================================
# 3. COGNITIVE REFRAMING WIDGET
# ============================================================
class CognitiveReframingWidget(BaseExerciseWidget):
    """Shows negative thoughts transforming into positive ones."""
    STEPS = [
        ("Identify the thought", "What negative thought do you have?", 12),
        ("I'm going to fail...", "Notice this negative pattern", 12),
        ("Challenge it", "Is this based on facts or feelings?", 12),
        ("Reframe it", "I've prepared well. I'll do my best.", 12),
        ("Practice", "Repeat the positive thought with belief", 12),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.cloud_alpha = 255
    
    def update_state(self):
        step_duration = 12.0
        self.current_step = min(int(self.time // step_duration), len(self.STEPS) - 1)
        self.step_progress = (self.time % step_duration) / step_duration
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background - transitions from dark to bright
        overall_progress = min(self.time / 60.0, 1.0)
        bg_r = int(15 + 25 * overall_progress)
        bg_g = int(15 + 35 * overall_progress)
        bg_b = int(40 + 20 * overall_progress)
        painter.fillRect(self.rect(), QColor(bg_r, bg_g, bg_b))
        
        step_title, step_sub, _ = self.STEPS[self.current_step]
        
        # Draw thought cloud
        cloud_cx, cloud_cy = cx, cy - 30
        cloud_w, cloud_h = 200, 100
        
        if self.current_step < 2:
            # Dark/negative thought cloud
            cloud_color = QColor(80, 40, 40, 200)
            text_color = QColor(255, 100, 100)
        elif self.current_step == 2:
            # Questioning - yellow
            mix = self.step_progress
            cloud_color = QColor(int(80 + 100 * mix), int(40 + 80 * mix), int(40 + 10 * mix), 200)
            text_color = QColor(255, 200, 100)
        else:
            # Positive - green/bright
            cloud_color = QColor(40, 120, 80, 200)
            text_color = QColor(150, 255, 200)
        
        # Draw cloud shape
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(cloud_color))
        path = QPainterPath()
        path.addEllipse(cloud_cx - 100, cloud_cy - 40, 200, 80)
        path.addEllipse(cloud_cx - 120, cloud_cy - 20, 80, 60)
        path.addEllipse(cloud_cx + 40, cloud_cy - 25, 90, 60)
        path.addEllipse(cloud_cx - 60, cloud_cy - 55, 120, 50)
        painter.drawPath(path)
        
        # Thought text inside cloud
        painter.setPen(QPen(text_color))
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(QRectF(cloud_cx - 90, cloud_cy - 25, 180, 50), 
                        Qt.AlignCenter | Qt.TextWordWrap, step_title)
        
        # Arrows between steps
        if self.current_step >= 2:
            painter.setPen(QPen(QColor(255, 255, 100, 150), 2))
            # Light rays from cloud
            for i in range(8):
                angle = (i / 8) * math.pi * 2 + self.time * 0.5
                ray_len = 30 + 20 * math.sin(self.time * 2 + i)
                x1 = cloud_cx + math.cos(angle) * 120
                y1 = cloud_cy + math.sin(angle) * 60
                x2 = cloud_cx + math.cos(angle) * (120 + ray_len)
                y2 = cloud_cy + math.sin(angle) * (60 + ray_len * 0.5)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Step indicator at bottom
        for i in range(len(self.STEPS)):
            dot_x = cx - 60 + i * 30
            dot_y = h - 80
            if i <= self.current_step:
                painter.setBrush(QBrush(QColor(100, 200, 150)))
            else:
                painter.setBrush(QBrush(QColor(60, 60, 80)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(dot_x, dot_y), 8, 8)
        
        # Sub text
        self.draw_sub_text(painter, step_sub, h // 2 - 100, 14, QColor(200, 200, 200))
        
        # Step number
        self.draw_text_at(painter, f"Step {self.current_step + 1}/5", 20, 30, 12, QColor(150, 150, 150))
        painter.end()


# ============================================================
# 4. BOX BREATHING (4-4-4-4) WIDGET
# ============================================================
class BoxBreathingWidget(BaseExerciseWidget):
    """Traces a square: Inhale 4s, Hold 4s, Exhale 4s, Hold 4s. Cycle=16s, ~3.75 cycles."""
    PHASES = [("INHALE", 4), ("HOLD", 4), ("EXHALE", 4), ("HOLD", 4)]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase_idx = 0
        self.dot_pos = (0, 0)
    
    def update_state(self):
        cycle = 16.0
        t = self.time % cycle
        if t < 4:
            self.phase_idx = 0
            self.phase_progress = t / 4.0
        elif t < 8:
            self.phase_idx = 1
            self.phase_progress = (t - 4) / 4.0
        elif t < 12:
            self.phase_idx = 2
            self.phase_progress = (t - 8) / 4.0
        else:
            self.phase_idx = 3
            self.phase_progress = (t - 12) / 4.0
        
        self.phase_text = self.PHASES[self.phase_idx][0]
        self.count = int((t % 4)) + 1
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background
        grad = QRadialGradient(cx, cy, max(w, h) * 0.7)
        grad.setColorAt(0, QColor(15, 25, 55))
        grad.setColorAt(1, QColor(5, 10, 25))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Box parameters
        box_size = min(w, h) * 0.45
        bx = cx - box_size / 2
        by = cy - box_size / 2
        
        # Draw box outline
        painter.setPen(QPen(QColor(60, 80, 120), 2, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRectF(bx, by, box_size, box_size))
        
        # Corner labels
        corners = [
            (bx, by, "Start"),
            (bx + box_size, by, "Inhale"),
            (bx + box_size, by + box_size, "Hold"),
            (bx, by + box_size, "Exhale"),
        ]
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QPen(QColor(120, 140, 180)))
        for x, y, label in corners:
            painter.drawText(int(x - 20), int(y - 10), label)
        
        # Trace progress along the box - lit path
        colors = [QColor(33, 150, 243), QColor(156, 39, 176), QColor(76, 175, 80), QColor(255, 193, 7)]
        color = colors[self.phase_idx]
        
        # Calculate dot position on the box
        p = self.phase_progress
        if self.phase_idx == 0:  # Right side going up... actually let's go: top-left to top-right
            dx = bx + p * box_size
            dy = by
        elif self.phase_idx == 1:  # top-right to bottom-right
            dx = bx + box_size
            dy = by + p * box_size
        elif self.phase_idx == 2:  # bottom-right to bottom-left
            dx = bx + box_size - p * box_size
            dy = by + box_size
        else:  # bottom-left to top-left
            dx = bx
            dy = by + box_size - p * box_size
        
        # Draw traced path (lit segment)
        painter.setPen(QPen(color, 4))
        if self.phase_idx == 0:
            painter.drawLine(int(bx), int(by), int(dx), int(dy))
        elif self.phase_idx == 1:
            painter.drawLine(int(bx), int(by), int(bx + box_size), int(by))
            painter.drawLine(int(bx + box_size), int(by), int(dx), int(dy))
        elif self.phase_idx == 2:
            painter.drawLine(int(bx), int(by), int(bx + box_size), int(by))
            painter.drawLine(int(bx + box_size), int(by), int(bx + box_size), int(by + box_size))
            painter.drawLine(int(bx + box_size), int(by + box_size), int(dx), int(dy))
        else:
            painter.drawLine(int(bx), int(by), int(bx + box_size), int(by))
            painter.drawLine(int(bx + box_size), int(by), int(bx + box_size), int(by + box_size))
            painter.drawLine(int(bx + box_size), int(by + box_size), int(bx), int(by + box_size))
            painter.drawLine(int(bx), int(by + box_size), int(dx), int(dy))
        
        # Glowing dot
        glow = QRadialGradient(dx, dy, 20)
        glow.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 200))
        glow.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(dx, dy), 20, 20)
        
        # Solid dot
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(dx, dy), 8, 8)
        
        # Phase text center
        self.draw_centered_text(painter, self.phase_text, 0, 28, color)
        self.draw_centered_text(painter, str(self.count), 40, 22, QColor(200, 200, 200))
        
        cycle_num = int(self.time // 16) + 1
        self.draw_text_at(painter, f"Box Breathing  •  Cycle {cycle_num}", 20, 30, 12, QColor(120, 120, 120))
        painter.end()


# ============================================================
# 5. GROUNDING 5-4-3-2-1 WIDGET
# ============================================================
class Grounding54321Widget(BaseExerciseWidget):
    """5 senses countdown: 5 See, 4 Touch, 3 Hear, 2 Smell, 1 Taste."""
    SENSES = [
        ("👁 SEE", "Name 5 things you can see", 5, QColor(100, 180, 255)),
        ("✋ TOUCH", "Name 4 things you can feel", 4, QColor(255, 180, 100)),
        ("👂 HEAR", "Name 3 things you can hear", 3, QColor(180, 100, 255)),
        ("👃 SMELL", "Name 2 things you can smell", 2, QColor(100, 255, 180)),
        ("👅 TASTE", "Name 1 thing you can taste", 1, QColor(255, 100, 150)),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_sense = 0
    
    def update_state(self):
        step_duration = 12.0  # 12s per sense = 60s
        self.current_sense = min(int(self.time // step_duration), 4)
        self.step_progress = (self.time % step_duration) / step_duration
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        sense_name, instruction, count, color = self.SENSES[self.current_sense]
        
        # Background transitions
        bg_intensity = 0.1 + 0.05 * self.current_sense
        painter.fillRect(self.rect(), QColor(int(20 * bg_intensity * 10), 
                                              int(25 * bg_intensity * 10), 
                                              int(40 * bg_intensity * 10)))
        
        # Central countdown number
        big_num = 5 - self.current_sense
        painter.setPen(Qt.NoPen)
        
        # Pulsing glow behind number
        pulse = 0.8 + 0.2 * math.sin(self.time * 3)
        glow_r = 80 * pulse
        glow = QRadialGradient(cx, cy, glow_r)
        glow.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 100))
        glow.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPointF(cx, cy), glow_r, glow_r)
        
        # Big number
        painter.setPen(QPen(color))
        painter.setFont(QFont("Arial", 80, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, str(big_num))
        
        # Sense icon and name above
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.drawText(QRectF(0, cy - 120, w, 40), Qt.AlignCenter, sense_name)
        
        # Instruction below
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(QRectF(0, cy + 60, w, 30), Qt.AlignCenter, instruction)
        
        # Item dots - show how many items to name
        dot_y = cy + 110
        total_dots = count
        for i in range(total_dots):
            dot_x = cx - (total_dots - 1) * 15 + i * 30
            filled = (self.step_progress * total_dots) > i
            if filled:
                painter.setBrush(QBrush(color))
            else:
                painter.setBrush(QBrush(QColor(60, 60, 80)))
            painter.setPen(QPen(color.darker(150), 1))
            painter.drawEllipse(QPointF(dot_x, dot_y), 10, 10)
        
        # Progress: sense indicators at bottom
        for i in range(5):
            ix = cx - 80 + i * 40
            iy = h - 50
            _, _, _, sc = self.SENSES[i]
            if i < self.current_sense:
                painter.setBrush(QBrush(sc))
            elif i == self.current_sense:
                painter.setBrush(QBrush(sc.lighter(130)))
            else:
                painter.setBrush(QBrush(QColor(50, 50, 70)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(ix - 12, iy, 24, 6), 3, 3)
        
        self.draw_text_at(painter, "5-4-3-2-1 Grounding", 20, 30, 12, QColor(120, 120, 120))
        painter.end()


# ============================================================
# 6. BODY SCAN MEDITATION WIDGET
# ============================================================
class BodyScanWidget(BaseExerciseWidget):
    """Body outline with a scanning beam moving from feet to head."""
    BODY_PARTS = [
        ("Feet & Toes", 0.95),
        ("Calves & Knees", 0.82),
        ("Thighs", 0.72),
        ("Hips & Lower Back", 0.62),
        ("Abdomen", 0.52),
        ("Chest", 0.42),
        ("Shoulders & Arms", 0.35),
        ("Neck", 0.25),
        ("Face & Head", 0.14),
        ("Whole Body", 0.50),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scan_position = 0.95
        self.current_part = 0
    
    def update_state(self):
        part_duration = 6.0  # 6s per part = 60s
        self.current_part = min(int(self.time // part_duration), len(self.BODY_PARTS) - 1)
        _, y_ratio = self.BODY_PARTS[self.current_part]
        self.scan_position = y_ratio
        self.step_progress = (self.time % part_duration) / part_duration
        self.phase_text = self.BODY_PARTS[self.current_part][0]
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Dark calm background
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(10, 15, 35))
        grad.setColorAt(1, QColor(20, 10, 30))
        painter.fillRect(self.rect(), QBrush(grad))
        
        body_x = cx
        body_top = h * 0.08
        body_h = h * 0.82
        
        # Body silhouette (simple outline)
        painter.setPen(QPen(QColor(60, 90, 130), 2))
        painter.setBrush(Qt.NoBrush)
        
        # Head
        head_r = body_h * 0.055
        head_cy = body_top + head_r * 1.2
        painter.drawEllipse(QPointF(body_x, head_cy), head_r, head_r * 1.15)
        
        # Neck
        neck_y = head_cy + head_r * 1.2
        painter.drawLine(int(body_x - head_r * 0.4), int(neck_y - head_r * 0.3),
                        int(body_x - head_r * 0.4), int(neck_y + head_r * 0.3))
        painter.drawLine(int(body_x + head_r * 0.4), int(neck_y - head_r * 0.3),
                        int(body_x + head_r * 0.4), int(neck_y + head_r * 0.3))
        
        # Torso
        shoulder_y = neck_y + head_r * 0.4
        hip_y = body_top + body_h * 0.55
        sw = body_h * 0.14
        hw = body_h * 0.09
        painter.drawLine(int(body_x - sw), int(shoulder_y), int(body_x + sw), int(shoulder_y))
        painter.drawLine(int(body_x - sw), int(shoulder_y), int(body_x - hw), int(hip_y))
        painter.drawLine(int(body_x + sw), int(shoulder_y), int(body_x + hw), int(hip_y))
        
        # Arms
        arm_y = body_top + body_h * 0.50
        painter.drawLine(int(body_x - sw), int(shoulder_y), int(body_x - sw * 2), int(arm_y))
        painter.drawLine(int(body_x + sw), int(shoulder_y), int(body_x + sw * 2), int(arm_y))
        
        # Legs
        leg_y = body_top + body_h * 0.95
        painter.drawLine(int(body_x - hw), int(hip_y), int(body_x - hw * 1.5), int(leg_y))
        painter.drawLine(int(body_x + hw), int(hip_y), int(body_x + hw * 1.5), int(leg_y))
        
        # Scanning beam
        scan_y = body_top + body_h * self.scan_position
        beam_width = sw * 3
        
        # Beam glow
        pulse = 0.7 + 0.3 * math.sin(self.time * 4)
        beam_color = QColor(80, 200, 255, int(120 * pulse))
        beam_grad = QLinearGradient(body_x - beam_width, scan_y, body_x + beam_width, scan_y)
        beam_grad.setColorAt(0, QColor(80, 200, 255, 0))
        beam_grad.setColorAt(0.3, beam_color)
        beam_grad.setColorAt(0.7, beam_color)
        beam_grad.setColorAt(1, QColor(80, 200, 255, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(beam_grad))
        painter.drawRect(QRectF(body_x - beam_width, scan_y - 15, beam_width * 2, 30))
        
        # Beam center line
        painter.setPen(QPen(QColor(100, 220, 255, 200), 2))
        painter.drawLine(int(body_x - beam_width * 0.8), int(scan_y),
                        int(body_x + beam_width * 0.8), int(scan_y))
        
        # Part label
        self.draw_centered_text(painter, f"Focus: {self.phase_text}", -h // 2 + 35, 20, QColor(100, 220, 255))
        self.draw_sub_text(painter, "Breathe into this area... notice any sensations...", h // 2 - 70, 13, QColor(160, 160, 180))
        
        self.draw_text_at(painter, f"Body Scan  •  Area {self.current_part + 1}/{len(self.BODY_PARTS)}", 20, 30, 11, QColor(100, 100, 120))
        painter.end()


# ============================================================
# 7. DEEP BREATHING WIDGET
# ============================================================
class DeepBreathingWidget(BaseExerciseWidget):
    """Belly breathing: Inhale 4s (belly rises), Exhale 6s (belly falls). Cycle=10s, 6 cycles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.belly_size = 0.0
    
    def update_state(self):
        cycle = 10.0
        t = self.time % cycle
        if t < 4:
            self.phase = "INHALE"
            self.phase_progress = t / 4.0
            self.belly_size = self.phase_progress
            self.count = int(t) + 1
            self.sub_text = f"Breathe in slowly through nose... {self.count}"
        else:
            self.phase = "EXHALE"
            self.phase_progress = (t - 4) / 6.0
            self.belly_size = 1.0 - self.phase_progress
            self.count = int(t - 4) + 1
            self.sub_text = f"Breathe out slowly through mouth... {self.count}"
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Calm blue background
        grad = QRadialGradient(cx, cy, max(w, h) * 0.7)
        grad.setColorAt(0, QColor(20, 35, 60))
        grad.setColorAt(1, QColor(8, 15, 35))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Draw lungs representation
        lung_w = 60 + self.belly_size * 30
        lung_h = 80 + self.belly_size * 40
        lung_offset = 50
        
        # Left lung
        lung_color = QColor(70, 140, 200, 150)
        painter.setBrush(QBrush(lung_color))
        painter.setPen(QPen(QColor(100, 170, 230), 2))
        painter.drawEllipse(QPointF(cx - lung_offset, cy - 40), lung_w * 0.7, lung_h)
        
        # Right lung
        painter.drawEllipse(QPointF(cx + lung_offset, cy - 40), lung_w * 0.7, lung_h)
        
        # Belly/diaphragm
        belly_r = 70 + self.belly_size * 50
        belly_color = QColor(100, 200, 150, int(100 + self.belly_size * 80))
        painter.setBrush(QBrush(belly_color))
        painter.setPen(QPen(QColor(130, 220, 170), 2))
        painter.drawEllipse(QPointF(cx, cy + 60), belly_r, belly_r * 0.6)
        
        # Hand indicators (on chest and belly)
        painter.setPen(QPen(QColor(200, 200, 200, 150), 1))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(int(cx - 15), int(cy - 80), "Chest")
        painter.drawText(int(cx - 15), int(cy + 65), "Belly ↑")
        
        # Arrow showing belly movement
        if self.phase == "INHALE":
            arrow_dir = -1  # up
            arrow_color = QColor(100, 200, 255)
        else:
            arrow_dir = 1  # down
            arrow_color = QColor(100, 255, 150)
        
        painter.setPen(QPen(arrow_color, 3))
        arrow_x = cx + 100
        arrow_y = cy + 60
        painter.drawLine(arrow_x, arrow_y - 20, arrow_x, arrow_y + 20)
        if arrow_dir == -1:
            painter.drawLine(arrow_x, arrow_y - 20, arrow_x - 8, arrow_y - 10)
            painter.drawLine(arrow_x, arrow_y - 20, arrow_x + 8, arrow_y - 10)
        else:
            painter.drawLine(arrow_x, arrow_y + 20, arrow_x - 8, arrow_y + 10)
            painter.drawLine(arrow_x, arrow_y + 20, arrow_x + 8, arrow_y + 10)
        
        # Phase and count
        color = QColor(100, 200, 255) if self.phase == "INHALE" else QColor(100, 255, 150)
        self.draw_centered_text(painter, self.phase, -h // 2 + 50, 28, color)
        self.draw_sub_text(painter, self.sub_text, h // 2 - 80, 14, QColor(180, 180, 200))
        
        cycle_num = int(self.time // 10) + 1
        self.draw_text_at(painter, f"Deep Breathing  •  Cycle {cycle_num}/6", 20, 30, 11, QColor(100, 100, 130))
        painter.end()


# ============================================================
# 8. MINDFUL WALKING WIDGET
# ============================================================
class MindfulWalkingWidget(BaseExerciseWidget):
    """Footsteps appearing on a path with focus cues."""
    FOCUS_CUES = [
        "Feel your left foot touch the ground",
        "Feel your right foot lift and step",
        "Notice the weight shifting",
        "Feel the ground beneath you",
        "Notice your breathing rhythm",
        "Feel each toe pressing down",
        "Notice the air on your skin",
        "Feel the rhythm of your steps",
        "Sense your body moving through space",
        "Notice the balance in each step",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.footsteps = []
        self.step_side = 0  # 0=left, 1=right
    
    def update_state(self):
        step_interval = 3.0
        total_steps = int(self.time // step_interval)
        
        while len(self.footsteps) < total_steps + 1 and len(self.footsteps) < 20:
            side = len(self.footsteps) % 2
            self.footsteps.append({
                'side': side,
                'time': len(self.footsteps) * step_interval,
                'cue': self.FOCUS_CUES[len(self.footsteps) % len(self.FOCUS_CUES)]
            })
        
        cue_idx = min(int(self.time // 6), len(self.FOCUS_CUES) - 1)
        self.sub_text = self.FOCUS_CUES[cue_idx]
        self.step_side = total_steps % 2
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Nature path background
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(30, 50, 30))
        grad.setColorAt(1, QColor(20, 35, 20))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Draw the path
        path_color = QColor(120, 100, 70, 100)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(path_color))
        path = QPainterPath()
        path.moveTo(cx - 60, h)
        path.lineTo(cx + 60, h)
        path.lineTo(cx + 30, 0)
        path.lineTo(cx - 30, 0)
        path.closeSubpath()
        painter.drawPath(path)
        
        # Draw footsteps (perspective: bottom=close, top=far)
        for i, step in enumerate(self.footsteps):
            age = self.time - step['time']
            if age < 0:
                continue
            
            # Position: starts at bottom and scrolls up
            y_pos = h - 80 - i * 40
            if y_pos < 50:
                continue
            
            # Perspective: smaller as they go up
            scale = 0.4 + 0.6 * (y_pos / h)
            x_offset = 20 if step['side'] == 0 else -20
            x_pos = cx + int(x_offset * scale)
            
            # Fade in
            alpha = min(255, int(age * 200))
            foot_color = QColor(200, 180, 140, alpha)
            
            # Draw footprint shape
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(foot_color))
            
            foot_w = int(12 * scale)
            foot_h = int(22 * scale)
            painter.drawEllipse(QPointF(x_pos, y_pos), foot_w, foot_h)
            
            # Toes
            for t in range(-2, 3):
                toe_x = x_pos + t * int(4 * scale)
                toe_y = y_pos - foot_h - int(3 * scale)
                painter.drawEllipse(QPointF(toe_x, toe_y), int(3 * scale), int(3 * scale))
        
        # Current step highlight
        pulse = 0.6 + 0.4 * math.sin(self.time * 4)
        highlight_color = QColor(150, 255, 150, int(100 * pulse))
        step_x = cx + (20 if self.step_side == 0 else -20)
        glow = QRadialGradient(step_x, h - 80, 40)
        glow.setColorAt(0, highlight_color)
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPointF(step_x, h - 80), 40, 40)
        
        # Focus cue
        self.draw_centered_text(painter, "MINDFUL WALKING", -h // 2 + 40, 22, QColor(150, 220, 150))
        self.draw_sub_text(painter, self.sub_text, h // 2 - 90, 14, QColor(180, 200, 180))
        
        step_count = len([s for s in self.footsteps if self.time >= s['time']])
        self.draw_text_at(painter, f"Steps: {step_count}", 20, 30, 11, QColor(100, 130, 100))
        painter.end()


# ============================================================
# 9. GRATITUDE PRACTICE WIDGET
# ============================================================
class GratitudePracticeWidget(BaseExerciseWidget):
    """Hearts growing, gratitude prompts rotating."""
    PROMPTS = [
        "Think of someone who helped you recently...",
        "What is one thing that made you smile today?",
        "Name something about your body you're grateful for...",
        "Think of a place that makes you feel safe...",
        "What skill or ability are you thankful for?",
        "Who in your life brings you joy?",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hearts = []
        self.current_prompt = 0
    
    def update_state(self):
        prompt_duration = 10.0
        self.current_prompt = min(int(self.time // prompt_duration), len(self.PROMPTS) - 1)
        self.step_progress = (self.time % prompt_duration) / prompt_duration
        
        # Add hearts periodically
        if int(self.time * 2) > len(self.hearts):
            self.hearts.append({
                'x': random.uniform(0.2, 0.8),
                'y': random.uniform(0.3, 0.7),
                'size': random.uniform(0.5, 1.5),
                'phase': random.uniform(0, 6.28),
                'born': self.time
            })
    
    def draw_heart(self, painter, cx, cy, size, color):
        path = QPainterPath()
        s = size * 15
        path.moveTo(cx, cy + s * 0.4)
        path.cubicTo(cx - s, cy - s * 0.3, cx - s * 0.5, cy - s, cx, cy - s * 0.5)
        path.cubicTo(cx + s * 0.5, cy - s, cx + s, cy - s * 0.3, cx, cy + s * 0.4)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPath(path)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Warm background
        grad = QRadialGradient(cx, cy, max(w, h) * 0.7)
        grad.setColorAt(0, QColor(50, 20, 30))
        grad.setColorAt(1, QColor(25, 10, 20))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Draw floating hearts
        for heart in self.hearts:
            age = self.time - heart['born']
            alpha = min(200, int(age * 100))
            float_y = math.sin(self.time * 1.5 + heart['phase']) * 10
            
            hx = int(heart['x'] * w)
            hy = int(heart['y'] * h + float_y)
            
            color = QColor(255, 80, 120, alpha)
            self.draw_heart(painter, hx, hy, heart['size'], color)
        
        # Central glowing heart
        pulse = 1.0 + 0.15 * math.sin(self.time * 2)
        main_size = 3.0 * pulse
        glow_color = QColor(255, 100, 130, 60)
        self.draw_heart(painter, cx, cy - 20, main_size * 1.3, glow_color)
        self.draw_heart(painter, cx, cy - 20, main_size, QColor(255, 80, 120, 200))
        
        # Prompt text
        prompt = self.PROMPTS[self.current_prompt]
        painter.setPen(QPen(QColor(255, 220, 230)))
        painter.setFont(QFont("Arial", 15))
        painter.drawText(QRectF(40, h - 120, w - 80, 60), Qt.AlignCenter | Qt.TextWordWrap, prompt)
        
        self.draw_centered_text(painter, "GRATITUDE", -h // 2 + 40, 22, QColor(255, 180, 200))
        
        self.draw_text_at(painter, f"Reflection {self.current_prompt + 1}/{len(self.PROMPTS)}", 20, 30, 11, QColor(150, 100, 120))
        painter.end()


# ============================================================
# 10. VISUALIZATION TECHNIQUE WIDGET
# ============================================================
class VisualizationWidget(BaseExerciseWidget):
    """Peaceful scene building: sky, water, mountains, trees appear gradually."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_progress = 0.0
    
    def update_state(self):
        self.scene_progress = min(self.time / 55.0, 1.0)  # builds over 55s, hold 5s
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p = self.scene_progress
        
        # Sky - darkish at start, bright and blue at full
        sky_r = int(30 + 100 * p)
        sky_g = int(40 + 140 * p)
        sky_b = int(80 + 150 * min(p, 0.8))
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(sky_r, sky_g, sky_b))
        grad.setColorAt(0.6, QColor(sky_r + 30, sky_g + 20, sky_b - 20))
        grad.setColorAt(1, QColor(30, 80, 50))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Sun (appears after 20%)
        if p > 0.2:
            sun_alpha = min(255, int((p - 0.2) * 400))
            sun_color = QColor(255, 220, 80, sun_alpha)
            painter.setBrush(QBrush(sun_color))
            painter.setPen(Qt.NoPen)
            sun_y = int(h * 0.15 + (1 - p) * 50)
            painter.drawEllipse(QPointF(w * 0.75, sun_y), 35, 35)
            
            # Sun rays
            glow = QRadialGradient(w * 0.75, sun_y, 80)
            glow.setColorAt(0, QColor(255, 220, 80, int(sun_alpha * 0.3)))
            glow.setColorAt(1, QColor(255, 220, 80, 0))
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QPointF(w * 0.75, sun_y), 80, 80)
        
        # Mountains (appear after 15%)
        if p > 0.15:
            mt_alpha = min(255, int((p - 0.15) * 400))
            painter.setPen(Qt.NoPen)
            # Mountain 1
            painter.setBrush(QBrush(QColor(60, 80, 100, mt_alpha)))
            mt = QPainterPath()
            mt.moveTo(0, h * 0.55)
            mt.lineTo(w * 0.25, h * 0.2)
            mt.lineTo(w * 0.5, h * 0.55)
            mt.closeSubpath()
            painter.drawPath(mt)
            
            # Mountain 2
            painter.setBrush(QBrush(QColor(70, 90, 110, mt_alpha)))
            mt2 = QPainterPath()
            mt2.moveTo(w * 0.3, h * 0.55)
            mt2.lineTo(w * 0.6, h * 0.25)
            mt2.lineTo(w * 0.9, h * 0.55)
            mt2.closeSubpath()
            painter.drawPath(mt2)
        
        # Water (appears after 35%)
        if p > 0.35:
            water_alpha = min(200, int((p - 0.35) * 350))
            water_y = h * 0.55
            water_color = QColor(40, 100, 160, water_alpha)
            painter.setBrush(QBrush(water_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRectF(0, water_y, w, h * 0.2))
            
            # Ripples
            painter.setPen(QPen(QColor(80, 150, 200, int(water_alpha * 0.5)), 1))
            for i in range(5):
                ry = water_y + 10 + i * 15
                wave = math.sin(self.time * 2 + i * 0.5) * 20
                painter.drawLine(int(wave + 30), int(ry), int(w - 30 + wave), int(ry))
        
        # Trees (appear after 50%)
        if p > 0.5:
            tree_alpha = min(255, int((p - 0.5) * 500))
            for tx in [w * 0.1, w * 0.2, w * 0.8, w * 0.9]:
                # Trunk
                painter.setBrush(QBrush(QColor(80, 50, 30, tree_alpha)))
                painter.setPen(Qt.NoPen)
                painter.drawRect(QRectF(tx - 4, h * 0.45, 8, h * 0.12))
                
                # Leaves
                painter.setBrush(QBrush(QColor(40, 120, 60, tree_alpha)))
                painter.drawEllipse(QPointF(tx, h * 0.40), 20, 25)
        
        # Ground
        ground_color = QColor(40, 100, 50, int(200 * min(p * 2, 1)))
        painter.setBrush(QBrush(ground_color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRectF(0, h * 0.75, w, h * 0.25))
        
        # Flowers on ground (appear after 70%)
        if p > 0.7:
            flower_alpha = min(255, int((p - 0.7) * 800))
            for i in range(8):
                fx = w * 0.1 + i * w * 0.1
                fy = h * 0.80 + math.sin(i * 1.5) * 10
                colors = [QColor(255, 100, 150, flower_alpha), QColor(255, 200, 50, flower_alpha),
                         QColor(200, 100, 255, flower_alpha), QColor(255, 150, 80, flower_alpha)]
                painter.setBrush(QBrush(colors[i % 4]))
                painter.drawEllipse(QPointF(fx, fy), 6, 6)
        
        # Instruction text
        if p < 0.3:
            text = "Close your eyes... imagine a peaceful place..."
        elif p < 0.5:
            text = "See the mountains and sky forming..."
        elif p < 0.7:
            text = "Hear the gentle water... feel the breeze..."
        elif p < 0.9:
            text = "Smell the flowers... feel the warm sun..."
        else:
            text = "Stay in this peaceful place... breathe..."
        
        # Text box at bottom
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
        painter.drawRoundedRect(QRectF(30, h - 70, w - 60, 45), 10, 10)
        
        painter.setPen(QPen(QColor(230, 230, 240)))
        painter.setFont(QFont("Arial", 13))
        painter.drawText(QRectF(40, h - 65, w - 80, 35), Qt.AlignCenter, text)
        
        self.draw_text_at(painter, "Visualization", 20, 30, 12, QColor(150, 150, 180))
        painter.end()


# ============================================================
# 11. POSITIVE AFFIRMATIONS WIDGET
# ============================================================
class PositiveAffirmationsWidget(BaseExerciseWidget):
    """Rotating affirmation text with growing sun rays."""
    AFFIRMATIONS = [
        "I am capable and strong",
        "I handle challenges with grace",
        "I am worthy of good things",
        "I believe in myself",
        "I am at peace with who I am",
        "I choose to focus on what I can control",
        "I am enough, just as I am",
        "Every day I grow stronger",
        "I deserve happiness and love",
        "I trust my journey",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_affirmation = 0
    
    def update_state(self):
        duration = 6.0  # 6s per affirmation, 10 affirmations = 60s
        self.current_affirmation = min(int(self.time // duration), len(self.AFFIRMATIONS) - 1)
        self.step_progress = (self.time % duration) / duration
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Warm golden background
        overall = min(self.time / 50.0, 1.0)
        grad = QRadialGradient(cx, cy - 50, max(w, h) * 0.7)
        grad.setColorAt(0, QColor(int(60 + 40 * overall), int(40 + 30 * overall), int(15 + 15 * overall)))
        grad.setColorAt(1, QColor(20, 15, 10))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Sun rays from center
        ray_count = 12
        for i in range(ray_count):
            angle = (i / ray_count) * math.pi * 2 + self.time * 0.3
            ray_len = 100 + 80 * overall + 20 * math.sin(self.time * 2 + i)
            
            x1 = cx + math.cos(angle) * 40
            y1 = (cy - 40) + math.sin(angle) * 40
            x2 = cx + math.cos(angle) * ray_len
            y2 = (cy - 40) + math.sin(angle) * ray_len
            
            alpha = int(40 + 60 * overall)
            painter.setPen(QPen(QColor(255, 200, 80, alpha), 2))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Central sun
        sun_r = 35 + 10 * overall
        glow = QRadialGradient(cx, cy - 40, sun_r * 2)
        glow.setColorAt(0, QColor(255, 220, 100, 120))
        glow.setColorAt(1, QColor(255, 200, 50, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy - 40), sun_r * 2, sun_r * 2)
        
        painter.setBrush(QBrush(QColor(255, 210, 80)))
        painter.drawEllipse(QPointF(cx, cy - 40), sun_r, sun_r)
        
        # Affirmation text - fade in
        text = self.AFFIRMATIONS[self.current_affirmation]
        fade = min(1.0, self.step_progress * 4) * (1 - max(0, (self.step_progress - 0.8) * 5))
        fade = max(0, min(1, fade))
        alpha = int(255 * fade)
        
        painter.setPen(QPen(QColor(255, 240, 200, alpha)))
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        painter.drawText(QRectF(40, cy + 40, w - 80, 60), Qt.AlignCenter | Qt.TextWordWrap, f'"{text}"')
        
        # Instruction
        painter.setPen(QPen(QColor(200, 180, 140)))
        painter.setFont(QFont("Arial", 12))
        painter.drawText(QRectF(0, cy + 110, w, 30), Qt.AlignCenter, "Repeat with feeling and belief...")
        
        self.draw_text_at(painter, f"Affirmation {self.current_affirmation + 1}/{len(self.AFFIRMATIONS)}", 20, 30, 11, QColor(120, 100, 80))
        painter.end()


# ============================================================
# 12. JOURNALING WIDGET
# ============================================================
class JournalingWidget(BaseExerciseWidget):
    """Pen writing animation with journaling prompts."""
    PROMPTS = [
        "What happened today that affected you?",
        "How did that make you feel?",
        "What thoughts came with those feelings?",
        "What patterns do you notice?",
        "What can you learn from this?",
        "Write one kind thing about yourself...",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_prompt = 0
        self.lines_written = []
    
    def update_state(self):
        duration = 10.0
        self.current_prompt = min(int(self.time // duration), len(self.PROMPTS) - 1)
        self.step_progress = (self.time % duration) / duration
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        
        # Paper/notebook background
        painter.fillRect(self.rect(), QColor(250, 245, 230))
        
        # Notebook lines
        painter.setPen(QPen(QColor(200, 210, 230), 1))
        line_start_y = 120
        line_spacing = 35
        for i in range(15):
            y = line_start_y + i * line_spacing
            painter.drawLine(60, y, w - 60, y)
        
        # Red margin line
        painter.setPen(QPen(QColor(220, 150, 150), 1))
        painter.drawLine(80, 80, 80, h - 40)
        
        # Title at top
        painter.setPen(QPen(QColor(80, 80, 100)))
        painter.setFont(QFont("Arial", 18, QFont.Bold))
        painter.drawText(QRectF(90, 30, w - 180, 40), Qt.AlignCenter, "My Journal")
        
        # Current prompt
        prompt = self.PROMPTS[self.current_prompt]
        painter.setPen(QPen(QColor(100, 120, 160)))
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(QRectF(90, 75, w - 180, 35), Qt.AlignLeft | Qt.AlignVCenter, f"💭 {prompt}")
        
        # Simulated writing animation
        # Show "handwritten" lines appearing
        lines_to_show = int(self.step_progress * 6)
        writing_texts = [
            "Today I noticed that...",
            "I felt a sense of...",
            "When I think about it...",
            "I realize that I can...",
            "Moving forward, I want to...",
            "I am grateful for..."
        ]
        
        painter.setFont(QFont("Comic Sans MS", 12))
        painter.setPen(QPen(QColor(50, 50, 80)))
        
        for i in range(min(lines_to_show, 6)):
            y = line_start_y + i * line_spacing - 5
            text = writing_texts[i]
            
            # Partial reveal of current line
            if i == lines_to_show - 1:
                char_progress = (self.step_progress * 6 - i)
                chars_to_show = int(len(text) * char_progress)
                text = text[:chars_to_show]
            
            painter.drawText(90, y, text)
        
        # Pen cursor
        if lines_to_show > 0 and lines_to_show <= 6:
            pen_line = min(lines_to_show - 1, 5)
            pen_y = line_start_y + pen_line * line_spacing - 5
            char_progress = (self.step_progress * 6 - pen_line)
            pen_x = 90 + int(char_progress * 200)
            
            # Pen icon
            blink = int(self.time * 3) % 2
            if blink:
                painter.setPen(QPen(QColor(50, 50, 150), 2))
                painter.drawLine(pen_x, pen_y - 10, pen_x, pen_y + 5)
        
        # Progress dots
        for i in range(len(self.PROMPTS)):
            dx = w // 2 - 50 + i * 20
            dy = h - 40
            if i <= self.current_prompt:
                painter.setBrush(QBrush(QColor(100, 120, 180)))
            else:
                painter.setBrush(QBrush(QColor(200, 200, 210)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(dx, dy), 5, 5)
        
        self.draw_text_at(painter, f"Prompt {self.current_prompt + 1}/{len(self.PROMPTS)}", 20, h - 30, 10, QColor(150, 150, 150))
        painter.end()


# ============================================================
# 13. MUSIC THERAPY WIDGET
# ============================================================
class MusicTherapyWidget(BaseExerciseWidget):
    """Sound wave / equalizer visualization with calming instructions."""
    INSTRUCTIONS = [
        "Find a comfortable position...",
        "Close your eyes and listen...",
        "Focus on the melody...",
        "Notice each instrument...",
        "Let the music wash over you...",
        "Feel the rhythm in your body...",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bars = [0.0] * 32
        self.current_instruction = 0
    
    def update_state(self):
        duration = 10.0
        self.current_instruction = min(int(self.time // duration), len(self.INSTRUCTIONS) - 1)
        
        # Animate equalizer bars
        for i in range(len(self.bars)):
            target = 0.2 + 0.6 * abs(math.sin(self.time * (1.5 + i * 0.15) + i * 0.5))
            self.bars[i] += (target - self.bars[i]) * 0.1
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Dark background
        painter.fillRect(self.rect(), QColor(15, 12, 25))
        
        # Sound wave (sine wave)
        painter.setPen(QPen(QColor(80, 150, 255, 100), 2))
        wave_y = cy - 80
        for x in range(0, w, 2):
            y1 = wave_y + math.sin(x * 0.02 + self.time * 3) * 30 * math.sin(self.time * 0.5)
            y2 = wave_y + math.sin((x + 2) * 0.02 + self.time * 3) * 30 * math.sin(self.time * 0.5)
            painter.drawLine(x, int(y1), x + 2, int(y2))
        
        # Equalizer bars
        num_bars = len(self.bars)
        bar_width = (w - 100) / num_bars
        bar_gap = 2
        eq_y = cy + 20
        max_bar_h = 150
        
        for i, val in enumerate(self.bars):
            bx = 50 + i * bar_width
            bh = val * max_bar_h
            
            # Color gradient: blue to purple to pink
            t = i / num_bars
            r = int(80 + 175 * t)
            g = int(100 - 50 * t)
            b = int(255 - 100 * t)
            
            bar_color = QColor(r, g, b, 200)
            painter.setBrush(QBrush(bar_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(bx + bar_gap, eq_y - bh, bar_width - bar_gap * 2, bh), 2, 2)
            
            # Mirror below (reflection)
            ref_color = QColor(r, g, b, 60)
            painter.setBrush(QBrush(ref_color))
            painter.drawRoundedRect(QRectF(bx + bar_gap, eq_y + 5, bar_width - bar_gap * 2, bh * 0.4), 2, 2)
        
        # Musical notes floating
        for i in range(6):
            note_x = (w * 0.15 + i * w * 0.14) + math.sin(self.time * 1.2 + i * 2) * 20
            note_y = 80 + math.sin(self.time * 0.8 + i * 1.5) * 30
            
            painter.setPen(QPen(QColor(200, 180, 255, 120)))
            painter.setFont(QFont("Arial", 18))
            notes = ["♪", "♫", "♩", "♬", "♪", "♫"]
            painter.drawText(int(note_x), int(note_y), notes[i])
        
        # Instruction
        text = self.INSTRUCTIONS[self.current_instruction]
        painter.setPen(QPen(QColor(180, 170, 220)))
        painter.setFont(QFont("Arial", 15))
        painter.drawText(QRectF(0, h - 80, w, 30), Qt.AlignCenter, text)
        
        self.draw_text_at(painter, "Music Therapy", 20, 30, 12, QColor(100, 90, 130))
        painter.end()


# ============================================================
# 14. PHYSICAL EXERCISE WIDGET
# ============================================================
class PhysicalExerciseWidget(BaseExerciseWidget):
    """Stick figure doing exercises with heart rate visual."""
    EXERCISES = [
        ("Arm Circles", "Rotate arms in circles"),
        ("Marching", "March in place, lift knees"),
        ("Side Steps", "Step side to side"),
        ("Shoulder Shrugs", "Shrug shoulders up and down"),
        ("Gentle Squats", "Bend knees slightly"),
        ("Cool Down", "Slow breaths, gentle sway"),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_exercise = 0
        self.heart_rate = 70
    
    def update_state(self):
        duration = 10.0
        self.current_exercise = min(int(self.time // duration), len(self.EXERCISES) - 1)
        self.step_progress = (self.time % duration) / duration
        
        # Simulated heart rate
        if self.current_exercise < 5:
            self.heart_rate = 70 + self.current_exercise * 8 + math.sin(self.time * 2) * 5
        else:
            self.heart_rate = 80 - (self.time - 50) * 2
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Energetic background
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0, QColor(20, 30, 50))
        grad.setColorAt(1, QColor(30, 20, 40))
        painter.fillRect(self.rect(), QBrush(grad))
        
        exercise_name, instruction = self.EXERCISES[self.current_exercise]
        
        # Draw stick figure
        fig_x, fig_y = cx, cy
        head_r = 20
        t = self.time * 3  # animation speed
        
        # Head
        painter.setPen(QPen(QColor(200, 220, 255), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(fig_x, fig_y - 80), head_r, head_r)
        
        # Body
        painter.drawLine(fig_x, int(fig_y - 60), fig_x, int(fig_y + 20))
        
        # Animated limbs based on exercise
        if self.current_exercise == 0:  # Arm Circles
            arm_angle = t * 2
            lx = fig_x + int(math.cos(arm_angle) * 50)
            ly = fig_y - 30 + int(math.sin(arm_angle) * 50)
            rx = fig_x + int(math.cos(arm_angle + math.pi) * 50)
            ry = fig_y - 30 + int(math.sin(arm_angle + math.pi) * 50)
            painter.drawLine(fig_x, int(fig_y - 50), lx, ly)
            painter.drawLine(fig_x, int(fig_y - 50), rx, ry)
            # Trail
            painter.setPen(QPen(QColor(100, 150, 255, 60), 1, Qt.DashLine))
            painter.drawEllipse(QPointF(fig_x, fig_y - 30), 50, 50)
        elif self.current_exercise == 1:  # Marching
            leg_phase = math.sin(t * 2)
            left_knee = fig_y + 20 + min(0, leg_phase * 40)
            right_knee = fig_y + 20 + min(0, -leg_phase * 40)
            painter.setPen(QPen(QColor(200, 220, 255), 3))
            painter.drawLine(fig_x - 5, int(fig_y + 20), fig_x - 15, int(left_knee + 40))
            painter.drawLine(fig_x + 5, int(fig_y + 20), fig_x + 15, int(right_knee + 40))
            # Arms swing
            painter.drawLine(fig_x, int(fig_y - 50), fig_x - 30, int(fig_y - 20 - leg_phase * 15))
            painter.drawLine(fig_x, int(fig_y - 50), fig_x + 30, int(fig_y - 20 + leg_phase * 15))
        elif self.current_exercise == 2:  # Side Steps
            side = math.sin(t) * 40
            painter.setPen(QPen(QColor(200, 220, 255), 3))
            # Shift figure
            painter.drawLine(int(fig_x + side), int(fig_y + 20), int(fig_x + side - 20), int(fig_y + 70))
            painter.drawLine(int(fig_x + side), int(fig_y + 20), int(fig_x + side + 20), int(fig_y + 70))
            painter.drawLine(int(fig_x + side), int(fig_y - 50), int(fig_x + side - 30), int(fig_y - 20))
            painter.drawLine(int(fig_x + side), int(fig_y - 50), int(fig_x + side + 30), int(fig_y - 20))
        elif self.current_exercise == 3:  # Shoulder Shrugs
            shrug = abs(math.sin(t * 1.5)) * 15
            painter.setPen(QPen(QColor(200, 220, 255), 3))
            painter.drawLine(fig_x, int(fig_y - 50 - shrug), fig_x - 40, int(fig_y - 25 - shrug))
            painter.drawLine(fig_x, int(fig_y - 50 - shrug), fig_x + 40, int(fig_y - 25 - shrug))
            painter.drawLine(fig_x, int(fig_y + 20), fig_x - 15, int(fig_y + 70))
            painter.drawLine(fig_x, int(fig_y + 20), fig_x + 15, int(fig_y + 70))
        elif self.current_exercise == 4:  # Gentle Squats
            squat = abs(math.sin(t)) * 25
            painter.setPen(QPen(QColor(200, 220, 255), 3))
            painter.drawLine(fig_x, int(fig_y + 20 + squat), fig_x - 25, int(fig_y + 70 + squat * 0.3))
            painter.drawLine(fig_x, int(fig_y + 20 + squat), fig_x + 25, int(fig_y + 70 + squat * 0.3))
            painter.drawLine(fig_x, int(fig_y - 50 + squat), fig_x - 35, int(fig_y - 25 + squat))
            painter.drawLine(fig_x, int(fig_y - 50 + squat), fig_x + 35, int(fig_y - 25 + squat))
        else:  # Cool Down
            sway = math.sin(t * 0.5) * 10
            painter.setPen(QPen(QColor(200, 220, 255), 3))
            painter.drawLine(int(fig_x + sway), int(fig_y - 50), int(fig_x + sway - 35), int(fig_y - 15))
            painter.drawLine(int(fig_x + sway), int(fig_y - 50), int(fig_x + sway + 35), int(fig_y - 15))
            painter.drawLine(fig_x, int(fig_y + 20), fig_x - 15, int(fig_y + 70))
            painter.drawLine(fig_x, int(fig_y + 20), fig_x + 15, int(fig_y + 70))
        
        # Heart rate display
        hr = int(self.heart_rate)
        painter.setPen(QPen(QColor(255, 80, 80)))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(w - 120, 40, f"♥ {hr} BPM")
        
        # Heart rate wave
        painter.setPen(QPen(QColor(255, 80, 80, 150), 2))
        wave_y = 60
        for x in range(w - 130, w - 20):
            y1 = wave_y + math.sin((x + self.time * 100) * 0.1) * 10
            y2 = wave_y + math.sin((x + 1 + self.time * 100) * 0.1) * 10
            painter.drawLine(x, int(y1), x + 1, int(y2))
        
        # Exercise name and instruction
        self.draw_centered_text(painter, exercise_name, -h // 2 + 40, 22, QColor(100, 200, 255))
        self.draw_sub_text(painter, instruction, h // 2 - 80, 14, QColor(180, 190, 210))
        
        self.draw_text_at(painter, f"Exercise {self.current_exercise + 1}/{len(self.EXERCISES)}", 20, 30, 11, QColor(100, 100, 130))
        painter.end()


# ============================================================
# 15. SOCIAL CONNECTION WIDGET
# ============================================================
class SocialConnectionWidget(BaseExerciseWidget):
    """Two figures connected by a growing bridge/network."""
    STEPS = [
        "Think of someone you care about...",
        "Imagine reaching out to them...",
        "What would you say to them?",
        "Feel the warmth of connection...",
        "Plan to reach out today...",
        "You are not alone...",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.connection_strength = 0.0
    
    def update_state(self):
        duration = 10.0
        self.current_step = min(int(self.time // duration), len(self.STEPS) - 1)
        self.connection_strength = min(self.time / 50.0, 1.0)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background
        grad = QRadialGradient(cx, cy, max(w, h) * 0.6)
        grad.setColorAt(0, QColor(25, 25, 50))
        grad.setColorAt(1, QColor(10, 10, 25))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Two figures
        fig1_x = cx - 120
        fig2_x = cx + 120
        fig_y = cy + 20
        
        # Person 1
        painter.setPen(QPen(QColor(100, 180, 255), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(fig1_x, fig_y - 60), 18, 18)
        painter.drawLine(fig1_x, int(fig_y - 42), fig1_x, int(fig_y + 10))
        painter.drawLine(fig1_x, int(fig_y - 25), fig1_x - 25, int(fig_y + 5))
        painter.drawLine(fig1_x, int(fig_y - 25), fig1_x + 25, int(fig_y + 5))
        painter.drawLine(fig1_x, int(fig_y + 10), fig1_x - 15, int(fig_y + 50))
        painter.drawLine(fig1_x, int(fig_y + 10), fig1_x + 15, int(fig_y + 50))
        
        # Person 2
        painter.setPen(QPen(QColor(255, 150, 100), 3))
        painter.drawEllipse(QPointF(fig2_x, fig_y - 60), 18, 18)
        painter.drawLine(fig2_x, int(fig_y - 42), fig2_x, int(fig_y + 10))
        painter.drawLine(fig2_x, int(fig_y - 25), fig2_x - 25, int(fig_y + 5))
        painter.drawLine(fig2_x, int(fig_y - 25), fig2_x + 25, int(fig_y + 5))
        painter.drawLine(fig2_x, int(fig_y + 10), fig2_x - 15, int(fig_y + 50))
        painter.drawLine(fig2_x, int(fig_y + 10), fig2_x + 15, int(fig_y + 50))
        
        # Connection lines between them (growing)
        if self.connection_strength > 0:
            num_lines = int(self.connection_strength * 8) + 1
            for i in range(num_lines):
                alpha = int(100 + self.connection_strength * 155)
                y_off = -30 + i * 10
                wave = math.sin(self.time * 2 + i * 0.8) * 5
                
                color = QColor(200, 150, 255, alpha)
                painter.setPen(QPen(color, 2))
                painter.drawLine(fig1_x + 25, int(fig_y + y_off + wave),
                               fig2_x - 25, int(fig_y + y_off - wave))
            
            # Heart between them
            if self.connection_strength > 0.5:
                pulse = 1 + 0.1 * math.sin(self.time * 3)
                heart_alpha = int(min(255, (self.connection_strength - 0.5) * 500))
                painter.setPen(Qt.NoPen)
                color = QColor(255, 100, 130, heart_alpha)
                # Simple heart using paths
                path = QPainterPath()
                hs = 12 * pulse
                path.moveTo(cx, cy + hs * 0.4)
                path.cubicTo(cx - hs, cy - hs * 0.3, cx - hs * 0.5, cy - hs, cx, cy - hs * 0.5)
                path.cubicTo(cx + hs * 0.5, cy - hs, cx + hs, cy - hs * 0.3, cx, cy + hs * 0.4)
                painter.setBrush(QBrush(color))
                painter.drawPath(path)
        
        # Text
        text = self.STEPS[self.current_step]
        painter.setPen(QPen(QColor(200, 180, 230)))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(QRectF(40, h - 90, w - 80, 40), Qt.AlignCenter | Qt.TextWordWrap, text)
        
        self.draw_centered_text(painter, "SOCIAL CONNECTION", -h // 2 + 40, 20, QColor(180, 160, 230))
        self.draw_text_at(painter, f"Step {self.current_step + 1}/{len(self.STEPS)}", 20, 30, 11, QColor(100, 90, 120))
        painter.end()


# ============================================================
# 16. SLEEP HYGIENE WIDGET
# ============================================================
class SleepHygieneWidget(BaseExerciseWidget):
    """Night scene with moon and stars, calming tips."""
    TIPS = [
        "Set a consistent bedtime...",
        "Dim the lights around you...",
        "Put screens away 1 hour before bed...",
        "Keep your room cool and dark...",
        "Take slow, deep breaths...",
        "Let your mind grow quiet...",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stars = [(random.uniform(0.05, 0.95), random.uniform(0.05, 0.45),
                       random.uniform(0.5, 2.0), random.uniform(0, 6.28)) for _ in range(50)]
        self.current_tip = 0
    
    def update_state(self):
        duration = 10.0
        self.current_tip = min(int(self.time // duration), len(self.TIPS) - 1)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        
        # Night sky gradient
        darkness = min(self.time / 30.0, 1.0)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(int(10 * (1 - darkness * 0.5)), int(15 * (1 - darkness * 0.3)), int(40 - 15 * darkness)))
        grad.setColorAt(0.6, QColor(int(15 - 5 * darkness), int(20 - 5 * darkness), int(35 - 10 * darkness)))
        grad.setColorAt(1, QColor(15, 20, 30))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Stars - twinkle
        for sx, sy, size, phase in self.stars:
            twinkle = 0.4 + 0.6 * abs(math.sin(self.time * 1.5 + phase))
            alpha = int(200 * twinkle * min(self.time / 10, 1))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 230, alpha)))
            star_x = sx * w
            star_y = sy * h
            painter.drawEllipse(QPointF(star_x, star_y), size, size)
        
        # Moon
        moon_x = w * 0.75
        moon_y = h * 0.2
        moon_r = 35
        
        # Moon glow
        glow = QRadialGradient(moon_x, moon_y, moon_r * 3)
        glow.setColorAt(0, QColor(200, 210, 255, 40))
        glow.setColorAt(1, QColor(200, 210, 255, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(moon_x, moon_y), moon_r * 3, moon_r * 3)
        
        # Moon body
        painter.setBrush(QBrush(QColor(230, 235, 255)))
        painter.drawEllipse(QPointF(moon_x, moon_y), moon_r, moon_r)
        
        # Moon craters (subtle)
        painter.setBrush(QBrush(QColor(210, 215, 235)))
        painter.drawEllipse(QPointF(moon_x - 8, moon_y - 5), 6, 6)
        painter.drawEllipse(QPointF(moon_x + 10, moon_y + 8), 4, 4)
        
        # Horizon hills
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(15, 25, 35)))
        hills = QPainterPath()
        hills.moveTo(0, h * 0.7)
        hills.cubicTo(w * 0.2, h * 0.6, w * 0.3, h * 0.65, w * 0.5, h * 0.62)
        hills.cubicTo(w * 0.7, h * 0.59, w * 0.8, h * 0.64, w, h * 0.68)
        hills.lineTo(w, h)
        hills.lineTo(0, h)
        hills.closeSubpath()
        painter.drawPath(hills)
        
        # Tip text
        tip = self.TIPS[self.current_tip]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.drawRoundedRect(QRectF(40, h - 90, w - 80, 50), 10, 10)
        
        painter.setPen(QPen(QColor(200, 210, 240)))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(QRectF(50, h - 85, w - 100, 40), Qt.AlignCenter, f"💤 {tip}")
        
        self.draw_text_at(painter, "Sleep Hygiene", 20, 30, 12, QColor(100, 110, 140))
        painter.end()


# ============================================================
# 17. NATURE THERAPY WIDGET
# ============================================================
class NatureTherapyWidget(BaseExerciseWidget):
    """Tree growing with leaves, birds, nature elements appearing."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.growth = 0.0
        self.leaves = []
        self.birds = []
    
    def update_state(self):
        self.growth = min(self.time / 45.0, 1.0)
        
        # Add leaves
        if self.growth > 0.3 and int(self.time * 3) > len(self.leaves):
            self.leaves.append({
                'angle': random.uniform(0, 6.28),
                'dist': random.uniform(0.4, 1.2),
                'size': random.uniform(0.6, 1.2),
                'color_var': random.uniform(-20, 20),
                'phase': random.uniform(0, 6.28)
            })
        
        # Add birds
        if self.growth > 0.6 and len(self.birds) < 4:
            if int(self.time) % 8 == 0 and len(self.birds) < int(self.time // 8):
                self.birds.append({
                    'x': random.uniform(-0.5, 0.2),
                    'y': random.uniform(0.1, 0.3),
                    'speed': random.uniform(0.002, 0.004),
                    'wing_speed': random.uniform(3, 5)
                })
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx = w // 2
        
        # Sky
        grad = QLinearGradient(0, 0, 0, h)
        sky_blue = min(self.growth * 1.5, 1.0)
        grad.setColorAt(0, QColor(int(60 + 100 * sky_blue), int(120 + 100 * sky_blue), int(180 + 50 * sky_blue)))
        grad.setColorAt(0.6, QColor(int(100 + 80 * sky_blue), int(160 + 60 * sky_blue), int(200 + 30 * sky_blue)))
        grad.setColorAt(1, QColor(60, 120, 50))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Ground
        painter.setPen(Qt.NoPen)
        ground_color = QColor(int(60 + 40 * self.growth), int(100 + 50 * self.growth), int(40 + 20 * self.growth))
        painter.setBrush(QBrush(ground_color))
        painter.drawRect(QRectF(0, h * 0.7, w, h * 0.3))
        
        # Tree trunk (grows up)
        trunk_height = h * 0.4 * self.growth
        trunk_width = 12 + 8 * self.growth
        trunk_bottom = h * 0.7
        trunk_top = trunk_bottom - trunk_height
        
        painter.setBrush(QBrush(QColor(100, 70, 40)))
        painter.drawRect(QRectF(cx - trunk_width / 2, trunk_top, trunk_width, trunk_height))
        
        # Branches
        if self.growth > 0.3:
            branch_progress = (self.growth - 0.3) / 0.7
            painter.setPen(QPen(QColor(90, 60, 35), 3))
            
            branches = [(-40, -20), (35, -30), (-30, -50), (25, -60)]
            for bx, by in branches:
                end_x = cx + int(bx * branch_progress)
                end_y = int(trunk_top + 30 + by * branch_progress)
                painter.drawLine(cx, int(trunk_top + 30 - by * 0.3), end_x, end_y)
        
        # Leaves
        if self.growth > 0.3:
            for leaf in self.leaves:
                sway = math.sin(self.time * 1.5 + leaf['phase']) * 5
                lx = cx + math.cos(leaf['angle']) * leaf['dist'] * 60 + sway
                ly = trunk_top - 10 + math.sin(leaf['angle']) * leaf['dist'] * 40
                
                g = int(min(255, 140 + leaf['color_var']))
                painter.setBrush(QBrush(QColor(50, g, 50, 200)))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPointF(lx, ly), 8 * leaf['size'], 6 * leaf['size'])
        
        # Birds
        for bird in self.birds:
            bx = (bird['x'] + self.time * bird['speed']) % 1.3 - 0.15
            by = bird['y'] + math.sin(self.time * 0.5 + bx * 5) * 0.02
            
            px = int(bx * w)
            py = int(by * h)
            wing = math.sin(self.time * bird['wing_speed']) * 8
            
            painter.setPen(QPen(QColor(40, 40, 50), 2))
            painter.drawLine(px - 10, py, px, int(py - wing))
            painter.drawLine(px, int(py - wing), px + 10, py)
        
        # Sun
        if self.growth > 0.2:
            sun_alpha = min(255, int((self.growth - 0.2) * 400))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 220, 80, sun_alpha)))
            painter.drawEllipse(QPointF(w * 0.8, h * 0.12), 30, 30)
        
        # Instruction
        if self.time < 15:
            text = "Step outside... feel the fresh air..."
        elif self.time < 30:
            text = "Notice the nature around you..."
        elif self.time < 45:
            text = "Breathe deeply... smell the earth..."
        else:
            text = "Feel connected to the natural world..."
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))
        painter.drawRoundedRect(QRectF(30, h - 70, w - 60, 40), 8, 8)
        painter.setPen(QPen(QColor(220, 230, 210)))
        painter.setFont(QFont("Arial", 13))
        painter.drawText(QRectF(40, h - 65, w - 80, 30), Qt.AlignCenter, f"🌿 {text}")
        
        self.draw_text_at(painter, "Nature Therapy", 20, 30, 12, QColor(80, 120, 80))
        painter.end()


# ============================================================
# 18. DIGITAL DETOX WIDGET
# ============================================================
class DigitalDetoxWidget(BaseExerciseWidget):
    """Phone screen fading away, nature/calm patterns emerging."""
    TIPS = [
        "Put your phone face down...",
        "Close unnecessary tabs...",
        "Take a break from screens...",
        "Look at something far away...",
        "Notice the world around you...",
        "Enjoy this moment of calm...",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tip = 0
        self.detox_progress = 0.0
    
    def update_state(self):
        duration = 10.0
        self.current_tip = min(int(self.time // duration), len(self.TIPS) - 1)
        self.detox_progress = min(self.time / 50.0, 1.0)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Background transitions from blue screen glow to natural calm
        dp = self.detox_progress
        grad = QRadialGradient(cx, cy, max(w, h) * 0.6)
        grad.setColorAt(0, QColor(int(30 - 15 * dp), int(30 + 20 * dp), int(60 - 20 * dp)))
        grad.setColorAt(1, QColor(int(10 + 5 * dp), int(15 + 15 * dp), int(30 - 10 * dp)))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Phone icon (fading out)
        phone_alpha = int(255 * (1 - dp))
        if phone_alpha > 5:
            # Phone body
            phone_w, phone_h = 80, 140
            px = cx - phone_w // 2
            py = cy - phone_h // 2 - 20
            
            painter.setPen(QPen(QColor(150, 150, 180, phone_alpha), 3))
            painter.setBrush(QBrush(QColor(30, 30, 50, phone_alpha)))
            painter.drawRoundedRect(QRectF(px, py, phone_w, phone_h), 10, 10)
            
            # Screen
            screen_margin = 8
            screen_color = QColor(50, 100, 200, int(phone_alpha * 0.6))
            painter.setBrush(QBrush(screen_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRectF(px + screen_margin, py + 20, phone_w - 2 * screen_margin, phone_h - 40))
            
            # Notification icons
            for i in range(3):
                painter.setBrush(QBrush(QColor(255, 80, 80, int(phone_alpha * 0.7))))
                painter.drawEllipse(QPointF(px + 20 + i * 20, py + 50), 4, 4)
            
            # X mark
            if dp > 0.3:
                cross_alpha = int(min(255, (dp - 0.3) * 500))
                painter.setPen(QPen(QColor(255, 80, 80, cross_alpha), 4))
                painter.drawLine(px + 10, py + 10, px + phone_w - 10, py + phone_h - 10)
                painter.drawLine(px + phone_w - 10, py + 10, px + 10, py + phone_h - 10)
        
        # Nature elements appearing
        if dp > 0.3:
            nature_alpha = int(min(255, (dp - 0.3) * 400))
            
            # Flowers
            flower_colors = [QColor(255, 150, 200, nature_alpha), QColor(255, 200, 100, nature_alpha),
                           QColor(180, 150, 255, nature_alpha)]
            for i, fc in enumerate(flower_colors):
                fx = cx - 100 + i * 100
                fy = cy + 80 + math.sin(self.time + i) * 5
                painter.setBrush(QBrush(fc))
                painter.setPen(Qt.NoPen)
                for p_angle in range(6):
                    a = (p_angle / 6) * math.pi * 2
                    px_petal = fx + math.cos(a) * 12
                    py_petal = fy + math.sin(a) * 12
                    painter.drawEllipse(QPointF(px_petal, py_petal), 6, 6)
                # Center
                painter.setBrush(QBrush(QColor(255, 230, 100, nature_alpha)))
                painter.drawEllipse(QPointF(fx, fy), 5, 5)
            
            # Butterflies
            if dp > 0.6:
                bf_alpha = int(min(255, (dp - 0.6) * 600))
                for i in range(2):
                    bx = cx + math.sin(self.time * 1.5 + i * 3) * 100
                    by = cy - 50 + math.cos(self.time * 1.2 + i * 2) * 40
                    wing = abs(math.sin(self.time * 5 + i)) * 10
                    
                    painter.setPen(QPen(QColor(200, 150, 255, bf_alpha), 1))
                    painter.drawLine(int(bx - wing), int(by - wing * 0.5), int(bx), int(by))
                    painter.drawLine(int(bx + wing), int(by - wing * 0.5), int(bx), int(by))
        
        # Tip text
        tip = self.TIPS[self.current_tip]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.drawRoundedRect(QRectF(40, h - 80, w - 80, 45), 10, 10)
        painter.setPen(QPen(QColor(200, 210, 230)))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(QRectF(50, h - 75, w - 100, 35), Qt.AlignCenter, f"📵 {tip}")
        
        self.draw_text_at(painter, "Digital Detox", 20, 30, 12, QColor(100, 110, 130))
        painter.end()


# ============================================================
# 19. HEALTHY EATING WIDGET
# ============================================================
class HealthyEatingWidget(BaseExerciseWidget):
    """Nutritional elements with mindful eating tips."""
    TIPS = [
        "Eating well fuels your mind...",
        "Notice what you eat today...",
        "Choose water over sugary drinks...",
        "Include colorful vegetables...",
        "Eat slowly and mindfully...",
        "Your body deserves nourishment...",
    ]
    FOODS = [
        ("🍎", QColor(220, 50, 50)),
        ("🥦", QColor(50, 160, 50)),
        ("🥕", QColor(240, 150, 30)),
        ("🫐", QColor(80, 60, 180)),
        ("🥑", QColor(80, 140, 50)),
        ("🍊", QColor(240, 160, 40)),
        ("🥬", QColor(60, 170, 60)),
        ("💧", QColor(80, 160, 255)),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tip = 0
        self.food_positions = []
        for i in range(len(self.FOODS)):
            angle = (i / len(self.FOODS)) * math.pi * 2
            self.food_positions.append({
                'angle': angle,
                'radius': 0.25,
                'phase': random.uniform(0, 6.28)
            })
    
    def update_state(self):
        duration = 10.0
        self.current_tip = min(int(self.time // duration), len(self.TIPS) - 1)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2 - 20
        
        # Background
        grad = QRadialGradient(cx, cy, max(w, h) * 0.6)
        grad.setColorAt(0, QColor(35, 40, 25))
        grad.setColorAt(1, QColor(15, 18, 10))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Plate circle
        plate_r = min(w, h) * 0.28
        painter.setPen(QPen(QColor(200, 200, 200, 100), 2))
        painter.setBrush(QBrush(QColor(240, 240, 230, 30)))
        painter.drawEllipse(QPointF(cx, cy), plate_r, plate_r)
        painter.drawEllipse(QPointF(cx, cy), plate_r * 0.85, plate_r * 0.85)
        
        # Food items orbiting
        for i, (emoji, color) in enumerate(self.FOODS):
            fp = self.food_positions[i]
            angle = fp['angle'] + self.time * 0.3
            bob = math.sin(self.time * 1.5 + fp['phase']) * 8
            
            radius = plate_r * 0.65
            fx = cx + math.cos(angle) * radius
            fy = cy + math.sin(angle) * radius * 0.6 + bob
            
            # Colored circle behind emoji
            appear_time = i * 3
            if self.time > appear_time:
                alpha = min(200, int((self.time - appear_time) * 80))
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), alpha)))
                painter.drawEllipse(QPointF(fx, fy), 22, 22)
                
                # Emoji text
                painter.setPen(QPen(QColor(255, 255, 255, alpha)))
                painter.setFont(QFont("Arial", 18))
                painter.drawText(QRectF(fx - 15, fy - 15, 30, 30), Qt.AlignCenter, emoji)
        
        # Center text: balanced diet
        painter.setPen(QPen(QColor(200, 220, 180)))
        painter.setFont(QFont("Arial", 12))
        painter.drawText(QRectF(cx - 60, cy - 12, 120, 24), Qt.AlignCenter, "Balanced\nNutrition")
        
        # Tip
        tip = self.TIPS[self.current_tip]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.drawRoundedRect(QRectF(40, h - 80, w - 80, 45), 10, 10)
        painter.setPen(QPen(QColor(200, 220, 180)))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(QRectF(50, h - 75, w - 100, 35), Qt.AlignCenter, tip)
        
        self.draw_text_at(painter, "Nutrition for Mental Health", 20, 30, 12, QColor(100, 120, 80))
        painter.end()


# ============================================================
# 20. GENTLE STRETCHING WIDGET
# ============================================================
class StretchingWidget(BaseExerciseWidget):
    """Stick figure doing stretches with guides and timers."""
    STRETCHES = [
        ("Neck Rolls", "Slowly roll your head in circles"),
        ("Shoulder Shrugs", "Raise shoulders to ears, hold, release"),
        ("Side Bend Left", "Reach left arm over, lean left"),
        ("Side Bend Right", "Reach right arm over, lean right"),
        ("Forward Fold", "Bend forward, relax neck and shoulders"),
        ("Deep Breath", "Stand tall, breathe deeply"),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_stretch = 0
    
    def update_state(self):
        duration = 10.0
        self.current_stretch = min(int(self.time // duration), len(self.STRETCHES) - 1)
        self.step_progress = (self.time % duration) / duration
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Calm background
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(25, 35, 50))
        grad.setColorAt(1, QColor(20, 25, 40))
        painter.fillRect(self.rect(), QBrush(grad))
        
        name, instruction = self.STRETCHES[self.current_stretch]
        t = self.time * 2
        
        # Stick figure base
        fig_x, fig_y = cx, cy + 20
        head_r = 18
        
        painter.setPen(QPen(QColor(150, 200, 255), 3))
        painter.setBrush(Qt.NoBrush)
        
        if self.current_stretch == 0:  # Neck Rolls
            angle = t * 1.5
            head_offset_x = math.sin(angle) * 10
            head_offset_y = math.cos(angle) * 8
            painter.drawEllipse(QPointF(fig_x + head_offset_x, fig_y - 75 + head_offset_y), head_r, head_r)
            # Guide circle
            painter.setPen(QPen(QColor(100, 150, 200, 80), 1, Qt.DashLine))
            painter.drawEllipse(QPointF(fig_x, fig_y - 75), 12, 10)
            painter.setPen(QPen(QColor(150, 200, 255), 3))
        elif self.current_stretch == 1:  # Shoulder Shrugs
            shrug = abs(math.sin(t * 0.8)) * 15
            painter.drawEllipse(QPointF(fig_x, fig_y - 75), head_r, head_r)
            painter.drawLine(fig_x, int(fig_y - 57), fig_x, int(fig_y + 15))
            painter.drawLine(fig_x, int(fig_y - 45 - shrug), fig_x - 40, int(fig_y - 20 - shrug))
            painter.drawLine(fig_x, int(fig_y - 45 - shrug), fig_x + 40, int(fig_y - 20 - shrug))
            # Arrow indicators
            painter.setPen(QPen(QColor(255, 200, 100, 150), 2))
            ay = int(fig_y - 40 - shrug)
            painter.drawLine(fig_x - 50, ay + 15, fig_x - 50, ay)
            painter.drawLine(fig_x + 50, ay + 15, fig_x + 50, ay)
        elif self.current_stretch == 2:  # Side Bend Left
            bend = math.sin(t * 0.6) * 0.5 + 0.5  # 0 to 1
            lean = bend * 25
            painter.drawEllipse(QPointF(fig_x - lean, fig_y - 75 - lean * 0.3), head_r, head_r)
            painter.drawLine(int(fig_x - lean * 0.5), int(fig_y - 55), fig_x, int(fig_y + 15))
            # Left arm reaching over
            painter.drawLine(fig_x, int(fig_y - 45), int(fig_x - 50 - lean), int(fig_y - 55 - lean * 0.5))
            painter.drawLine(fig_x, int(fig_y - 45), fig_x + 35, int(fig_y - 20))
        elif self.current_stretch == 3:  # Side Bend Right
            bend = math.sin(t * 0.6) * 0.5 + 0.5
            lean = bend * 25
            painter.drawEllipse(QPointF(fig_x + lean, fig_y - 75 - lean * 0.3), head_r, head_r)
            painter.drawLine(int(fig_x + lean * 0.5), int(fig_y - 55), fig_x, int(fig_y + 15))
            painter.drawLine(fig_x, int(fig_y - 45), int(fig_x + 50 + lean), int(fig_y - 55 - lean * 0.5))
            painter.drawLine(fig_x, int(fig_y - 45), fig_x - 35, int(fig_y - 20))
        elif self.current_stretch == 4:  # Forward Fold
            fold = math.sin(t * 0.5) * 0.5 + 0.5
            fold_angle = fold * 70
            # Body bends forward
            body_end_y = fig_y - 55 + fold_angle * 0.8
            body_end_x = fig_x + fold_angle * 0.3
            painter.drawEllipse(QPointF(body_end_x + 15, body_end_y - 10), head_r, head_r)
            painter.drawLine(fig_x, int(fig_y + 15), int(body_end_x), int(body_end_y))
            # Arms dangling
            painter.drawLine(int(body_end_x), int(body_end_y), int(body_end_x - 10), int(body_end_y + 35 * fold))
            painter.drawLine(int(body_end_x), int(body_end_y), int(body_end_x + 10), int(body_end_y + 35 * fold))
        else:  # Deep Breath
            breathe = math.sin(t * 0.8)
            expand = abs(breathe) * 8
            painter.drawEllipse(QPointF(fig_x, fig_y - 75), head_r, head_r)
            painter.drawLine(fig_x, int(fig_y - 57), fig_x, int(fig_y + 15))
            painter.drawLine(fig_x, int(fig_y - 45), fig_x - 40 - int(expand), int(fig_y - 10))
            painter.drawLine(fig_x, int(fig_y - 45), fig_x + 40 + int(expand), int(fig_y - 10))
            # Breath visual
            if breathe > 0:
                painter.setPen(QPen(QColor(100, 200, 255, int(breathe * 100)), 1))
                for i in range(3):
                    r = 20 + i * 15 + breathe * 10
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(QPointF(fig_x, fig_y - 30), r, r * 0.5)
        
        # Common: draw legs if not drawn
        if self.current_stretch not in [2, 3, 4]:
            painter.setPen(QPen(QColor(150, 200, 255), 3))
            painter.drawLine(fig_x, int(fig_y + 15), fig_x - 20, int(fig_y + 65))
            painter.drawLine(fig_x, int(fig_y + 15), fig_x + 20, int(fig_y + 65))
        else:
            painter.setPen(QPen(QColor(150, 200, 255), 3))
            painter.drawLine(fig_x, int(fig_y + 15), fig_x - 15, int(fig_y + 65))
            painter.drawLine(fig_x, int(fig_y + 15), fig_x + 15, int(fig_y + 65))
        
        # Hold timer circle
        timer_x = w - 60
        timer_y = 60
        timer_r = 25
        painter.setPen(QPen(QColor(60, 60, 80), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(timer_x, timer_y), timer_r, timer_r)
        
        # Timer arc
        span = int(-self.step_progress * 360 * 16)
        painter.setPen(QPen(QColor(100, 200, 150), 3))
        painter.drawArc(QRectF(timer_x - timer_r, timer_y - timer_r, timer_r * 2, timer_r * 2),
                       90 * 16, span)
        
        secs_left = int(10 - self.step_progress * 10)
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(QRectF(timer_x - 15, timer_y - 8, 30, 16), Qt.AlignCenter, str(secs_left))
        
        # Exercise name and instruction
        self.draw_centered_text(painter, name, -h // 2 + 40, 22, QColor(150, 200, 255))
        self.draw_sub_text(painter, instruction, h // 2 - 80, 14, QColor(170, 180, 200))
        
        self.draw_text_at(painter, f"Stretch {self.current_stretch + 1}/{len(self.STRETCHES)}", 20, 30, 11, QColor(100, 110, 130))
        painter.end()


# ============================================================
# 21. PROFESSIONAL SUPPORT WIDGET
# ============================================================
class ProfessionalSupportWidget(BaseExerciseWidget):
    """Informational: when to seek help, resources, supportive visuals."""
    MESSAGES = [
        ("It's okay to ask for help", "Seeking help is a sign of strength"),
        ("Talk to someone you trust", "A friend, family member, or counselor"),
        ("Professional help works", "Therapists are trained to support you"),
        ("You're not alone", "Many people seek mental health support"),
        ("Resources are available", "Helplines, counselors, online therapy"),
        ("Take the first step today", "Call, text, or visit a professional"),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_msg = 0
    
    def update_state(self):
        duration = 10.0
        self.current_msg = min(int(self.time // duration), len(self.MESSAGES) - 1)
        self.step_progress = (self.time % duration) / duration
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        
        # Warm supportive background
        grad = QRadialGradient(cx, cy, max(w, h) * 0.6)
        grad.setColorAt(0, QColor(30, 35, 55))
        grad.setColorAt(1, QColor(15, 18, 30))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Supporting hands visual
        hand_alpha = int(100 + 50 * math.sin(self.time))
        
        # Left hand
        painter.setPen(QPen(QColor(180, 150, 120, hand_alpha), 3))
        painter.setBrush(Qt.NoBrush)
        lh_path = QPainterPath()
        lh_path.moveTo(cx - 100, cy + 50)
        lh_path.cubicTo(cx - 80, cy + 20, cx - 50, cy, cx - 20, cy + 10)
        painter.drawPath(lh_path)
        
        # Right hand
        rh_path = QPainterPath()
        rh_path.moveTo(cx + 100, cy + 50)
        rh_path.cubicTo(cx + 80, cy + 20, cx + 50, cy, cx + 20, cy + 10)
        painter.drawPath(rh_path)
        
        # Warm glow in center (between hands)
        glow_pulse = 0.7 + 0.3 * math.sin(self.time * 1.5)
        glow = QRadialGradient(cx, cy + 20, 60 * glow_pulse)
        glow.setColorAt(0, QColor(255, 200, 100, 60))
        glow.setColorAt(1, QColor(255, 200, 100, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPointF(cx, cy + 20), 60, 60)
        
        # Shield/heart icon
        painter.setPen(Qt.NoPen)
        shield_color = QColor(100, 180, 220, int(180 * glow_pulse))
        painter.setBrush(QBrush(shield_color))
        shield = QPainterPath()
        shield.moveTo(cx, cy + 45)
        shield.cubicTo(cx - 25, cy + 25, cx - 30, cy - 5, cx, cy - 15)
        shield.cubicTo(cx + 30, cy - 5, cx + 25, cy + 25, cx, cy + 45)
        painter.drawPath(shield)
        
        # Plus/cross symbol inside
        painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
        painter.drawLine(cx, int(cy + 5), cx, int(cy + 30))
        painter.drawLine(int(cx - 12), int(cy + 17), int(cx + 12), int(cy + 17))
        
        # Message text
        title, subtitle = self.MESSAGES[self.current_msg]
        
        # Fade in/out
        fade = min(1.0, self.step_progress * 4) * (1 - max(0, (self.step_progress - 0.8) * 5))
        fade = max(0, min(1, fade))
        alpha = int(255 * fade)
        
        painter.setPen(QPen(QColor(200, 220, 255, alpha)))
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        painter.drawText(QRectF(40, cy - 100, w - 80, 40), Qt.AlignCenter, title)
        
        painter.setPen(QPen(QColor(170, 180, 200, alpha)))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(QRectF(40, cy - 60, w - 80, 30), Qt.AlignCenter, subtitle)
        
        # Helpline info at bottom
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.drawRoundedRect(QRectF(40, h - 75, w - 80, 45), 10, 10)
        painter.setPen(QPen(QColor(200, 200, 220)))
        painter.setFont(QFont("Arial", 11))
        painter.drawText(QRectF(50, h - 70, w - 100, 35), Qt.AlignCenter,
                        "📞 Talk to a professional • University counseling services are free")
        
        # Progress dots
        for i in range(len(self.MESSAGES)):
            dx = cx - 50 + i * 20
            dy = h - 25
            if i <= self.current_msg:
                painter.setBrush(QBrush(QColor(100, 180, 220)))
            else:
                painter.setBrush(QBrush(QColor(50, 55, 70)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(dx, dy), 4, 4)
        
        self.draw_text_at(painter, f"Step {self.current_msg + 1}/{len(self.MESSAGES)}", 20, 30, 11, QColor(100, 100, 130))
        painter.end()


# ============================================================
# WIDGET MAPPING - Maps technique IDs to their widget classes
# ============================================================
EXERCISE_WIDGETS = {
    "breathing_478": Breathing478Widget,
    "progressive_relaxation": ProgressiveRelaxationWidget,
    "cognitive_reframe": CognitiveReframingWidget,
    "box_breathing": BoxBreathingWidget,
    "grounding_54321": Grounding54321Widget,
    "body_scan": BodyScanWidget,
    "deep_breathing": DeepBreathingWidget,
    "mindful_walking": MindfulWalkingWidget,
    "gratitude_practice": GratitudePracticeWidget,
    "visualization": VisualizationWidget,
    "positive_affirmations": PositiveAffirmationsWidget,
    "journaling": JournalingWidget,
    "music_therapy": MusicTherapyWidget,
    "physical_exercise": PhysicalExerciseWidget,
    "social_connection": SocialConnectionWidget,
    "sleep_hygiene": SleepHygieneWidget,
    "time_in_nature": NatureTherapyWidget,
    "digital_detox": DigitalDetoxWidget,
    "healthy_eating": HealthyEatingWidget,
    "stretching": StretchingWidget,
    "professional_support": ProfessionalSupportWidget,
}

def get_exercise_widget(technique_id, parent=None):
    """Factory function to get the correct exercise widget for a technique."""
    widget_class = EXERCISE_WIDGETS.get(technique_id)
    if widget_class:
        return widget_class(parent)
    # Fallback to breathing widget if unknown technique
    return Breathing478Widget(parent)
