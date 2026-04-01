from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from OpenGL.GL import *
from OpenGL.GLU import *
import math


class JourneyWidget(QOpenGLWidget):
    """Interactive 3D journey visualization with clickable session points.
    
    Emits point_clicked(index) when user clicks on a session point.
    Shows before/after metrics, technique used, and improvement for each session.
    """
    
    point_clicked = pyqtSignal(int)
    
    def __init__(self, sessions, parent=None):
        super().__init__(parent)
        self.sessions = sessions
        self.camera_angle = 0
        self.time = 0
        self.points = []
        self.selected_index = -1
        self.hover_index = -1
        self.setMouseTracking(True)
        
        self.calculate_points()
        
        # Animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(20)
    
    def calculate_points(self):
        """Convert session data to rich 3D visualization points"""
        self.points = []
        
        for i, session in enumerate(self.sessions):
            initial = session.get('initial_metrics', {})
            final = session.get('final_metrics', {})
            improvement = session.get('improvement', {})
            
            # Calculate before/after wellbeing
            init_anxiety = initial.get('anxiety', 0.5)
            init_mood = initial.get('mood', 0.5)
            init_stress = initial.get('stress', 0.5)
            init_wellbeing = (1 - init_anxiety + init_mood + (1 - init_stress)) / 3
            
            fin_anxiety = final.get('anxiety', 0.5)
            fin_mood = final.get('mood', 0.5)
            fin_stress = final.get('stress', 0.5)
            fin_wellbeing = (1 - fin_anxiety + fin_mood + (1 - fin_stress)) / 3
            
            # Smooth spacing along X
            x = i * 5
            y = fin_wellbeing * 10  # Height = final wellbeing
            z = math.sin(i * 0.6) * 3  # Wavy path
            
            # Color gradient
            if fin_wellbeing < 0.25:
                color = [0.95, 0.15, 0.15]
            elif fin_wellbeing < 0.4:
                color = [1.0, 0.4, 0.1]
            elif fin_wellbeing < 0.55:
                color = [1.0, 0.65, 0.0]
            elif fin_wellbeing < 0.7:
                color = [0.9, 0.85, 0.1]
            elif fin_wellbeing < 0.85:
                color = [0.5, 0.85, 0.25]
            else:
                color = [0.2, 0.9, 0.3]
            
            # Size (newer = bigger)
            size = 0.45 + (i / max(1, len(self.sessions) - 1)) * 0.35
            
            # Technique name
            tech_id = session.get('technique', 'unknown')
            tech_name = self._format_tech_name(tech_id)
            
            # Date
            date_str = session.get('date', '')
            if date_str:
                try:
                    # Parse ISO date
                    date_display = date_str[:10]  # YYYY-MM-DD
                    time_display = date_str[11:16]  # HH:MM
                except (IndexError, ValueError):
                    date_display = date_str[:19]
                    time_display = ""
            else:
                date_display = f"Session {i + 1}"
                time_display = ""
            
            # Calculate improvement percentage
            anx_imp = improvement.get('anxiety', 0)
            mood_imp = improvement.get('mood', 0)
            stress_imp = improvement.get('stress', 0)
            overall_change = fin_wellbeing - init_wellbeing
            
            self.points.append({
                'position': [x, y, z],
                'color': color,
                'wellbeing': fin_wellbeing,
                'init_wellbeing': init_wellbeing,
                'size': size,
                'index': i,
                'technique': tech_name,
                'date': date_display,
                'time': time_display,
                'initial': initial,
                'final': final,
                'improvement': improvement,
                'overall_change': overall_change,
                'anxiety_change': anx_imp,
                'mood_change': mood_imp,
                'stress_change': stress_imp
            })
    
    def _format_tech_name(self, tech_id):
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
    
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLightfv(GL_LIGHT0, GL_POSITION, [20, 30, 20, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.55, 0.55, 0.55, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1])
        
        glLightfv(GL_LIGHT1, GL_POSITION, [-20, 20, 10, 1])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.35, 0.35, 0.4, 1])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.5, 0.5, 0.6, 1])
        
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glClearColor(0.92, 0.94, 0.98, 1.0)
    
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, w / h if h != 0 else 1, 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if not self.points:
            return
        
        # Center camera on path
        center_x = (len(self.points) - 1) * 5 / 2
        center_y = 5
        center_z = 0
        
        # Orbiting camera
        radius = 22 + len(self.points) * 1.2
        cam_a = math.radians(self.camera_angle)
        cam_x = center_x + radius * math.cos(cam_a)
        cam_z = center_z + radius * math.sin(cam_a)
        cam_y = 12 + math.sin(self.time * 0.001) * 1.5
        
        gluLookAt(cam_x, cam_y, cam_z,
                  center_x, center_y, center_z,
                  0, 1, 0)
        
        # Render layers
        self._draw_sky_gradient()
        self._draw_grid_floor()
        self._draw_terrain_markers()
        self._draw_journey_path()
        self._draw_vertical_bars()
        self._draw_journey_points()
        self._draw_connecting_beams()
        self._draw_particle_trail()
        self._draw_labels()
        
        # 2D text overlay using QPainter
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        self._draw_2d_overlay(painter)
        painter.end()
    
    def _draw_sky_gradient(self):
        """Soft sky background"""
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glBegin(GL_QUADS)
        glColor3f(0.75, 0.82, 0.95)
        glVertex3f(-1, 1, -0.99)
        glVertex3f(1, 1, -0.99)
        glColor3f(0.92, 0.94, 0.98)
        glVertex3f(1, -1, -0.99)
        glVertex3f(-1, -1, -0.99)
        glEnd()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def _draw_grid_floor(self):
        """Beautiful grid floor with gradient fading"""
        glDisable(GL_LIGHTING)
        glLineWidth(1.0)
        
        size = 50
        spacing = 5
        
        glBegin(GL_LINES)
        for i in range(-size, size + 1, spacing):
            alpha = max(0.05, 0.3 - abs(i) / size * 0.3)
            glColor4f(0.65, 0.7, 0.8, alpha)
            glVertex3f(i, -0.5, -size)
            glVertex3f(i, -0.5, size)
            glVertex3f(-size, -0.5, i)
            glVertex3f(size, -0.5, i)
        glEnd()
        
        # Subtle ground plane
        glColor4f(0.88, 0.9, 0.94, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-50, -0.51, -50)
        glVertex3f(50, -0.51, -50)
        glVertex3f(50, -0.51, 50)
        glVertex3f(-50, -0.51, 50)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _draw_terrain_markers(self):
        """Draw wellbeing level indicators"""
        glDisable(GL_LIGHTING)
        
        if not self.points:
            return
        
        max_x = (len(self.points) - 1) * 5 + 2
        min_x = -2
        
        # Wellbeing zones
        zones = [
            (0, 2.5, [0.95, 0.3, 0.3, 0.04], "Crisis"),
            (2.5, 5, [1.0, 0.65, 0.2, 0.04], "Low"),
            (5, 7.5, [0.95, 0.9, 0.3, 0.04], "Moderate"),
            (7.5, 10, [0.4, 0.85, 0.35, 0.04], "Good"),
        ]
        
        for y_low, y_high, color, label in zones:
            glColor4f(*color)
            glBegin(GL_QUADS)
            glVertex3f(min_x, y_low, -8)
            glVertex3f(max_x, y_low, -8)
            glVertex3f(max_x, y_high, -8)
            glVertex3f(min_x, y_high, -8)
            glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _draw_journey_path(self):
        """Draw smooth flowing path connecting points"""
        if len(self.points) < 2:
            return
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        
        # Wide glow path
        glLineWidth(14.0)
        glBegin(GL_LINE_STRIP)
        for pt in self.points:
            c = pt['color']
            glColor4f(c[0], c[1], c[2], 0.12)
            glVertex3f(*pt['position'])
        glEnd()
        
        # Medium path
        glLineWidth(6.0)
        glBegin(GL_LINE_STRIP)
        for i, pt in enumerate(self.points):
            c = pt['color']
            alpha = 0.5 + (i / len(self.points)) * 0.4
            glColor4f(c[0], c[1], c[2], alpha)
            glVertex3f(*pt['position'])
        glEnd()
        
        # Bright core
        glLineWidth(2.5)
        glBegin(GL_LINE_STRIP)
        for pt in self.points:
            c = pt['color']
            glColor4f(min(1, c[0] + 0.3), min(1, c[1] + 0.3), min(1, c[2] + 0.3), 0.8)
            glVertex3f(*pt['position'])
        glEnd()
        
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    def _draw_vertical_bars(self):
        """Draw vertical reference bars from floor to each point"""
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        
        for pt in self.points:
            pos = pt['position']
            c = pt['color']
            is_selected = pt['index'] == self.selected_index
            
            # Vertical line
            glLineWidth(2.0 if is_selected else 1.0)
            glBegin(GL_LINES)
            glColor4f(c[0], c[1], c[2], 0.6 if is_selected else 0.2)
            glVertex3f(pos[0], -0.5, pos[2])
            glColor4f(c[0], c[1], c[2], 0.8 if is_selected else 0.4)
            glVertex3f(pos[0], pos[1], pos[2])
            glEnd()
            
            # Ground circle
            glPushMatrix()
            glTranslatef(pos[0], -0.4, pos[2])
            glRotatef(-90, 1, 0, 0)
            glColor4f(c[0], c[1], c[2], 0.3 if is_selected else 0.12)
            q = gluNewQuadric()
            gluDisk(q, 0, 0.8 if is_selected else 0.5, 16, 1)
            gluDeleteQuadric(q)
            glPopMatrix()
        
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    def _draw_journey_points(self):
        """Draw beautiful spheres at each session point"""
        for pt in self.points:
            pos = pt['position']
            c = pt['color']
            size = pt['size']
            is_selected = pt['index'] == self.selected_index
            is_latest = pt['index'] == len(self.points) - 1
            
            glPushMatrix()
            glTranslatef(*pos)
            
            # Pulsing for selected/latest
            if is_selected:
                pulse = 1.0 + math.sin(self.time * 0.008) * 0.2
                size *= pulse
            elif is_latest:
                pulse = 1.0 + math.sin(self.time * 0.005) * 0.12
                size *= pulse
            
            # Outer glow layers
            glDisable(GL_LIGHTING)
            for j in range(4 if is_selected else 3):
                alpha = 0.18 - j * 0.04 if is_selected else 0.12 - j * 0.035
                glow_s = size + j * 0.25
                glColor4f(c[0], c[1], c[2], max(0, alpha))
                q = gluNewQuadric()
                gluSphere(q, glow_s, 20, 20)
                gluDeleteQuadric(q)
            glEnable(GL_LIGHTING)
            
            # Main sphere with shininess
            glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 100.0)
            glColor3f(*c)
            q = gluNewQuadric()
            gluQuadricNormals(q, GLU_SMOOTH)
            gluSphere(q, size, 24, 24)
            gluDeleteQuadric(q)
            
            # Bright inner core
            core = [min(1, x * 1.4) for x in c]
            glColor3f(*core)
            q = gluNewQuadric()
            gluSphere(q, size * 0.35, 14, 14)
            gluDeleteQuadric(q)
            
            # Sparkle for high wellbeing
            if pt['wellbeing'] > 0.7:
                self._draw_sparkle(size)
            
            # Selection ring
            if is_selected:
                glDisable(GL_LIGHTING)
                glColor4f(1, 1, 1, 0.6)
                glLineWidth(2.5)
                # Rotating ring
                ring_angle = self.time * 0.15
                glRotatef(ring_angle, 0, 1, 0)
                glBegin(GL_LINE_LOOP)
                for a in range(32):
                    angle = a * (2 * math.pi / 32)
                    glVertex3f(math.cos(angle) * (size + 0.3),
                               math.sin(angle) * (size + 0.3) * 0.3,
                               0)
                glEnd()
                glLineWidth(1.0)
                glEnable(GL_LIGHTING)
            
            # Before→After mini indicator
            if is_selected or is_latest:
                self._draw_change_indicator(pt, size)
            
            glPopMatrix()
    
    def _draw_sparkle(self, size):
        """Rotating sparkle cross"""
        glDisable(GL_LIGHTING)
        glColor4f(1, 1, 1, 0.7)
        glLineWidth(2.0)
        sa = self.time * 0.1
        for ang in [0, 60, 120]:
            glPushMatrix()
            glRotatef(ang + sa * 50, 0, 1, 0)
            glBegin(GL_LINES)
            glVertex3f(-size * 1.5, 0, 0)
            glVertex3f(size * 1.5, 0, 0)
            glVertex3f(0, -size * 1.5, 0)
            glVertex3f(0, size * 1.5, 0)
            glEnd()
            glPopMatrix()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    def _draw_change_indicator(self, pt, size):
        """Draw small up/down arrow showing improvement"""
        glDisable(GL_LIGHTING)
        change = pt['overall_change']
        
        glPushMatrix()
        glTranslatef(0, size + 0.5, 0)
        glRotatef(-self.camera_angle, 0, 1, 0)
        
        if change > 0.02:
            # Up arrow (improved)
            glColor4f(0.2, 0.9, 0.3, 0.9)
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0.4, 0)
            glVertex3f(-0.2, 0, 0)
            glVertex3f(0.2, 0, 0)
            glEnd()
        elif change < -0.02:
            # Down arrow (declined)
            glColor4f(0.9, 0.2, 0.2, 0.9)
            glBegin(GL_TRIANGLES)
            glVertex3f(0, -0.4, 0)
            glVertex3f(-0.2, 0, 0)
            glVertex3f(0.2, 0, 0)
            glEnd()
        else:
            # Steady line
            glColor4f(0.9, 0.9, 0.3, 0.7)
            glLineWidth(2.0)
            glBegin(GL_LINES)
            glVertex3f(-0.2, 0, 0)
            glVertex3f(0.2, 0, 0)
            glEnd()
            glLineWidth(1.0)
        
        glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def _draw_connecting_beams(self):
        """Draw tubes between consecutive points"""
        if len(self.points) < 2:
            return
        
        for i in range(len(self.points) - 1):
            p1 = self.points[i]['position']
            p2 = self.points[i + 1]['position']
            c1 = self.points[i]['color']
            c2 = self.points[i + 1]['color']
            color = [(c1[j] + c2[j]) / 2 for j in range(3)]
            
            glPushMatrix()
            
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dz = p2[2] - p1[2]
            length = math.sqrt(dx * dx + dy * dy + dz * dz)
            
            glTranslatef(p1[0], p1[1], p1[2])
            
            if length > 0.001:
                angle = math.degrees(math.acos(max(-1, min(1, dy / length))))
                if dx != 0 or dz != 0:
                    glRotatef(angle, -dz, 0, dx)
            
            glColor3f(*color)
            q = gluNewQuadric()
            gluQuadricNormals(q, GLU_SMOOTH)
            gluCylinder(q, 0.12, 0.12, length, 12, 1)
            gluDeleteQuadric(q)
            
            glPopMatrix()
    
    def _draw_particle_trail(self):
        """Floating particles along the path"""
        glDisable(GL_LIGHTING)
        glPointSize(3.5)
        
        glBegin(GL_POINTS)
        for i in range(len(self.points) - 1):
            p1 = self.points[i]['position']
            p2 = self.points[i + 1]['position']
            c = self.points[i]['color']
            
            for t in range(8):
                ratio = t / 8.0
                x = p1[0] + (p2[0] - p1[0]) * ratio
                y = p1[1] + (p2[1] - p1[1]) * ratio
                z = p1[2] + (p2[2] - p1[2]) * ratio
                
                float_y = math.sin(self.time * 0.002 + i + t * 0.15) * 0.35
                alpha = 0.35 + math.sin(self.time * 0.003 + t) * 0.2
                
                glColor4f(c[0], c[1], c[2], max(0, alpha))
                glVertex3f(x, y + float_y, z)
        glEnd()
        
        glPointSize(1.0)
        glEnable(GL_LIGHTING)
    
    def _draw_labels(self):
        """Draw floating labels for START and LATEST"""
        glDisable(GL_LIGHTING)
        
        if not self.points:
            return
        
        # START marker
        sp = self.points[0]['position']
        self._draw_marker_plate(sp, "START", [0.3, 0.5, 0.9], 1.0)
        
        # LATEST marker (pulsing)
        ep = self.points[-1]['position']
        pulse = 1.0 + math.sin(self.time * 0.005) * 0.15
        self._draw_marker_plate(ep, "LATEST", [0.2, 0.85, 0.3], pulse)
        
        # Session numbers for all points
        for pt in self.points:
            pos = pt['position']
            glPushMatrix()
            glTranslatef(pos[0], -0.3, pos[2])
            glRotatef(-self.camera_angle, 0, 1, 0)
            
            # Small number indicator
            c = pt['color']
            glColor4f(c[0], c[1], c[2], 0.7)
            glBegin(GL_QUADS)
            glVertex3f(-0.3, -0.15, 0)
            glVertex3f(0.3, -0.15, 0)
            glVertex3f(0.3, 0.15, 0)
            glVertex3f(-0.3, 0.15, 0)
            glEnd()
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
    
    def _draw_marker_plate(self, position, text, color, scale):
        glPushMatrix()
        glTranslatef(position[0], position[1] + 2.2, position[2])
        glRotatef(-self.camera_angle, 0, 1, 0)
        
        # Background plate
        s = 0.9 * scale
        glColor4f(color[0], color[1], color[2], 0.65)
        glBegin(GL_QUADS)
        glVertex3f(-s, -0.3, 0)
        glVertex3f(s, -0.3, 0)
        glVertex3f(s, 0.3, 0)
        glVertex3f(-s, 0.3, 0)
        glEnd()
        
        # Border
        glColor4f(1, 1, 1, 0.85)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-s, -0.3, 0)
        glVertex3f(s, -0.3, 0)
        glVertex3f(s, 0.3, 0)
        glVertex3f(-s, 0.3, 0)
        glEnd()
        
        # Connecting line down to point
        glColor4f(color[0], color[1], color[2], 0.4)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        glVertex3f(0, -0.3, 0)
        glVertex3f(0, -2.2, 0)
        glEnd()
        
        glPopMatrix()
    
    def _draw_info_panel(self, index):
        """Draw a detailed info panel for the selected session point"""
        if index < 0 or index >= len(self.points):
            return
        
        pt = self.points[index]
        pos = pt['position']
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glPushMatrix()
        glTranslatef(pos[0] + 1.5, pos[1] + 1.5, pos[2] + 1)
        glRotatef(-self.camera_angle, 0, 1, 0)
        
        # Panel dimensions
        pw, ph = 4.5, 5.0
        
        # Background panel with shadow
        glColor4f(0, 0, 0, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(0.1, -(ph + 0.1), -0.01)
        glVertex3f(pw + 0.1, -(ph + 0.1), -0.01)
        glVertex3f(pw + 0.1, 0.1, -0.01)
        glVertex3f(0.1, 0.1, -0.01)
        glEnd()
        
        # Main panel
        glColor4f(0.98, 0.98, 1.0, 0.92)
        glBegin(GL_QUADS)
        glVertex3f(0, -ph, 0)
        glVertex3f(pw, -ph, 0)
        glVertex3f(pw, 0, 0)
        glVertex3f(0, 0, 0)
        glEnd()
        
        # Header bar
        c = pt['color']
        glColor4f(c[0], c[1], c[2], 0.85)
        glBegin(GL_QUADS)
        glVertex3f(0, -0.7, 0.01)
        glVertex3f(pw, -0.7, 0.01)
        glVertex3f(pw, 0, 0.01)
        glVertex3f(0, 0, 0.01)
        glEnd()
        
        # Panel border
        glColor4f(c[0] * 0.7, c[1] * 0.7, c[2] * 0.7, 0.8)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(0, -ph, 0.01)
        glVertex3f(pw, -ph, 0.01)
        glVertex3f(pw, 0, 0.01)
        glVertex3f(0, 0, 0.01)
        glEnd()
        
        # Section dividers
        glColor4f(0.85, 0.85, 0.9, 0.5)
        glLineWidth(1.0)
        for div_y in [-1.6, -2.8, -3.8]:
            glBegin(GL_LINES)
            glVertex3f(0.2, div_y, 0.01)
            glVertex3f(pw - 0.2, div_y, 0.01)
            glEnd()
        
        # --- Content indicators (since we can't render text in OpenGL easily,
        #     use color-coded bars to show metrics) ---
        
        y_offset = -1.0
        bar_width = pw - 0.8
        bar_height = 0.15
        
        # Initial metrics bars
        init = pt['initial']
        final = pt['final']
        
        # Anxiety bar (initial vs final)
        self._draw_metric_bar(0.4, y_offset, bar_width, bar_height,
                              init.get('anxiety', 0.5), final.get('anxiety', 0.5),
                              [0.95, 0.3, 0.3], "anxiety")
        y_offset -= 0.45
        
        # Mood bar
        self._draw_metric_bar(0.4, y_offset, bar_width, bar_height,
                              init.get('mood', 0.5), final.get('mood', 0.5),
                              [0.3, 0.8, 0.4], "mood")
        y_offset -= 0.45
        
        # Stress bar
        self._draw_metric_bar(0.4, y_offset, bar_width, bar_height,
                              init.get('stress', 0.5), final.get('stress', 0.5),
                              [1.0, 0.65, 0.1], "stress")
        
        # Overall wellbeing indicator
        y_offset = -3.1
        wb = pt['wellbeing']
        glColor4f(c[0], c[1], c[2], 0.3)
        glBegin(GL_QUADS)
        glVertex3f(0.4, y_offset - 0.3, 0.01)
        glVertex3f(0.4 + bar_width * wb, y_offset - 0.3, 0.01)
        glVertex3f(0.4 + bar_width * wb, y_offset, 0.01)
        glVertex3f(0.4, y_offset, 0.01)
        glEnd()
        
        # Wellbeing border
        glColor4f(c[0], c[1], c[2], 0.7)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex3f(0.4, y_offset - 0.3, 0.01)
        glVertex3f(0.4 + bar_width, y_offset - 0.3, 0.01)
        glVertex3f(0.4 + bar_width, y_offset, 0.01)
        glVertex3f(0.4, y_offset, 0.01)
        glEnd()
        
        # Change arrows
        y_offset = -4.0
        changes = [
            (pt['anxiety_change'], [0.95, 0.3, 0.3]),
            (pt['mood_change'], [0.3, 0.8, 0.4]),
            (pt['stress_change'], [1.0, 0.65, 0.1])
        ]
        
        for ci, (change, col) in enumerate(changes):
            x_pos = 0.6 + ci * 1.3
            if abs(change) > 0.01:
                improved = (change > 0 and ci != 1) or (change > 0 and ci == 1)
                # For anxiety and stress, positive change = reduction = good
                # For mood, positive change = increase = good
                if improved:
                    glColor4f(0.2, 0.85, 0.3, 0.9)
                    # Up arrow
                    glBegin(GL_TRIANGLES)
                    glVertex3f(x_pos, y_offset + 0.3, 0.01)
                    glVertex3f(x_pos - 0.15, y_offset, 0.01)
                    glVertex3f(x_pos + 0.15, y_offset, 0.01)
                    glEnd()
                else:
                    glColor4f(0.9, 0.25, 0.2, 0.9)
                    # Down arrow
                    glBegin(GL_TRIANGLES)
                    glVertex3f(x_pos, y_offset - 0.3, 0.01)
                    glVertex3f(x_pos - 0.15, y_offset, 0.01)
                    glVertex3f(x_pos + 0.15, y_offset, 0.01)
                    glEnd()
            
            # Metric color dot
            glColor4f(col[0], col[1], col[2], 0.8)
            q = gluNewQuadric()
            glPushMatrix()
            glTranslatef(x_pos, y_offset - 0.5, 0.01)
            gluDisk(q, 0, 0.1, 10, 1)
            gluDeleteQuadric(q)
            glPopMatrix()
        
        glPopMatrix()
        glLineWidth(1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def _draw_metric_bar(self, x, y, width, height, initial, final, color, name):
        """Draw a before/after metric comparison bar"""
        # Initial (dimmer, background)
        glColor4f(color[0] * 0.5, color[1] * 0.5, color[2] * 0.5, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(x, y - height, 0.01)
        glVertex3f(x + width * initial, y - height, 0.01)
        glVertex3f(x + width * initial, y, 0.01)
        glVertex3f(x, y, 0.01)
        glEnd()
        
        # Final (brighter, foreground)
        glColor4f(color[0], color[1], color[2], 0.7)
        glBegin(GL_QUADS)
        glVertex3f(x, y - height * 0.6, 0.015)
        glVertex3f(x + width * final, y - height * 0.6, 0.015)
        glVertex3f(x + width * final, y + height * 0.1, 0.015)
        glVertex3f(x, y + height * 0.1, 0.015)
        glEnd()
        
        # Bar border
        glColor4f(color[0], color[1], color[2], 0.4)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x, y - height, 0.015)
        glVertex3f(x + width, y - height, 0.015)
        glVertex3f(x + width, y, 0.015)
        glVertex3f(x, y, 0.015)
        glEnd()
    
    def _draw_2d_overlay(self, painter):
        """Draw 2D text overlay for journey information with clickable point details"""
        w, h = self.width(), self.height()
        if not self.points:
            return
        
        # Top bar - session count
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 130))
        painter.drawRoundedRect(10, 10, 300, 36, 8, 8)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        painter.drawText(22, 34, f"Wellness Journey  \u2014  {len(self.points)} Sessions")
        
        # Selected point detail panel — fully responsive
        if self.selected_index >= 0 and self.selected_index < len(self.points):
            pt = self.points[self.selected_index]

            # Panel dimensions adapt to window size
            panel_w = min(320, w - 24)
            row_h   = max(34, min(44, h // 18))   # scales with window height
            header_h   = 52
            col_hdr_h  = 26
            sep_h      = 14
            well_h     = max(60, row_h + 22)
            hint_h     = 20
            content_h  = header_h + col_hdr_h + 3 * row_h + sep_h + well_h + hint_h + 10
            panel_h    = min(content_h, h - 26)

            px = w - panel_w - 12
            py = 12
            bar_w = panel_w - 22

            # Dark glass background
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(12, 12, 20, 215))
            painter.drawRoundedRect(px, py, panel_w, panel_h, 10, 10)

            # Clip all drawing to panel so nothing bleeds out
            painter.setClipRect(px, py, panel_w, panel_h)

            # Accent header bar
            c = pt['color']
            accent = QColor(int(c[0]*255), int(c[1]*255), int(c[2]*255))
            painter.setBrush(accent)
            painter.drawRoundedRect(px, py, panel_w, header_h - 8, 10, 10)
            painter.drawRect(px, py + header_h - 18, panel_w, 18)

            # Session title
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.drawText(px + 10, py + 22, f"Session {self.selected_index + 1}")

            # Technique name — elide if too long
            tech = pt.get('technique', 'Unknown')
            painter.setFont(QFont("Arial", 9))
            fm = painter.fontMetrics()
            max_tech_px = panel_w - 115
            tech_el = fm.elidedText(tech, Qt.ElideRight, max_tech_px)
            painter.drawText(px + 108, py + 22, tech_el)

            # Date/time row
            painter.setPen(QColor(200, 205, 220))
            painter.setFont(QFont("Arial", 9))
            date_str = f"{pt.get('date', '')}  {pt.get('time', '')}".strip()
            painter.drawText(px + 10, py + header_h - 4, date_str)

            # Column headers
            y = py + header_h + 12
            painter.setPen(QColor(150, 155, 175))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.drawText(px + 10,  y, "METRIC")
            painter.drawText(px + 94,  y, "BEFORE")
            painter.drawText(px + 160, y, "AFTER")
            painter.drawText(px + 224, y, "CHANGE")
            painter.setPen(QPen(QColor(55, 58, 78), 1))
            painter.drawLine(px + 10, y + 4, px + panel_w - 10, y + 4)
            y += col_hdr_h

            init  = pt.get('initial', {})
            final = pt.get('final',   {})
            rows  = [
                ("Anxiety", init.get('anxiety', 0.5), final.get('anxiety', 0.5), QColor(239, 83,  80),  True),
                ("Mood",    init.get('mood',    0.5), final.get('mood',    0.5), QColor(102, 187, 106), False),
                ("Stress",  init.get('stress',  0.5), final.get('stress',  0.5), QColor(255, 167, 38),  True),
            ]

            for name, bv, av, color, lower_better in rows:
                painter.setPen(color)
                painter.setFont(QFont("Arial", 9, QFont.Bold))
                painter.drawText(px + 10, y, name)

                painter.setPen(QColor(170, 170, 170))
                painter.setFont(QFont("Arial", 9))
                painter.drawText(px + 96,  y, f"{int(bv*100)}%")

                painter.setPen(QColor(220, 220, 220))
                painter.setFont(QFont("Arial", 9, QFont.Bold))
                painter.drawText(px + 162, y, f"{int(av*100)}%")

                diff     = bv - av if lower_better else av - bv
                raw_diff = av - bv
                sign     = "+" if raw_diff > 0 else ""
                chg_col  = QColor(76, 175, 80) if diff > 0.02 else QColor(244, 67, 54) if diff < -0.02 else QColor(200, 200, 100)
                painter.setPen(chg_col)
                painter.setFont(QFont("Arial", 9))
                painter.drawText(px + 226, y, f"{sign}{int(raw_diff*100)}%")

                # Dual progress bar (before = dim layer, after = bright layer)
                by2 = y + 5
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(38, 38, 50))
                painter.drawRoundedRect(px + 10, by2, bar_w, 4, 2, 2)
                painter.setBrush(QColor(color.red()//2, color.green()//2, color.blue()//2, 100))
                painter.drawRoundedRect(px + 10, by2, int(bar_w * bv), 4, 2, 2)
                painter.setBrush(color)
                painter.drawRoundedRect(px + 10, by2 + 1, int(bar_w * av), 2, 1, 1)

                y += row_h

            # Separator
            painter.setPen(QPen(QColor(55, 58, 78), 1))
            painter.drawLine(px + 10, y + 2, px + panel_w - 10, y + 2)
            y += sep_h

            # Overall wellbeing
            wb  = pt.get('wellbeing', 0.5)
            iwb = pt.get('init_wellbeing', 0.5)
            wbc = QColor(76, 175, 80) if wb > 0.6 else QColor(255, 235, 59) if wb > 0.4 else QColor(239, 83, 80)

            painter.setPen(QColor(200, 205, 225))
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.drawText(px + 10, y + 13, "Overall Wellbeing")

            painter.setPen(wbc)
            painter.setFont(QFont("Arial", 17, QFont.Bold))
            painter.drawText(px + 10, y + 36, f"{int(wb*100)}%")

            wbd  = wb - iwb
            ws   = "+" if wbd > 0 else ""
            wdc  = QColor(76, 175, 80) if wbd > 0.01 else QColor(244, 67, 54) if wbd < -0.01 else QColor(200, 200, 100)
            painter.setPen(wdc)
            painter.setFont(QFont("Arial", 9))
            painter.drawText(px + 68, y + 36, f"({ws}{int(wbd*100)}% vs start)")

            # Wellbeing fill bar
            bby = y + 42
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(38, 38, 50))
            painter.drawRoundedRect(px + 10, bby, bar_w, 5, 2, 2)
            painter.setBrush(wbc)
            painter.drawRoundedRect(px + 10, bby, int(bar_w * wb), 5, 2, 2)

            # Hint pinned to panel bottom
            painter.setPen(QColor(108, 110, 130))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(px + 10, py + panel_h - 5, "Click point again to deselect")

            painter.setClipping(False)
        else:
            # Passive click-hint at bottom-right
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 90))
            painter.drawRoundedRect(w - 215, h - 44, 203, 30, 6, 6)
            painter.setPen(QColor(200, 200, 210))
            painter.setFont(QFont("Arial", 9))
            painter.drawText(w - 205, h - 23, "Click a point for details")
    
    # ===== Interaction =====
    
    def mousePressEvent(self, event):
        """Handle click to select/deselect journey points"""
        if event.button() == Qt.LeftButton:
            clicked_idx = self._pick_point(event.x(), event.y())
            
            if clicked_idx >= 0:
                if self.selected_index == clicked_idx:
                    self.selected_index = -1  # Deselect
                else:
                    self.selected_index = clicked_idx
                self.point_clicked.emit(self.selected_index)
                self.update()
            else:
                if self.selected_index >= 0:
                    self.selected_index = -1
                    self.point_clicked.emit(-1)
                    self.update()
        
        super().mousePressEvent(event)
    
    def _pick_point(self, mouse_x, mouse_y):
        """Determine which point was clicked using OpenGL unprojection"""
        try:
            viewport = glGetIntegerv(GL_VIEWPORT)
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            
            # Flip Y for OpenGL coordinates
            win_y = viewport[3] - mouse_y
            
            best_idx = -1
            best_dist = float('inf')
            
            for pt in self.points:
                pos = pt['position']
                
                try:
                    # Project 3D point to screen
                    screen_x, screen_y, screen_z = gluProject(
                        pos[0], pos[1], pos[2],
                        modelview, projection, viewport
                    )
                    
                    # Check distance in screen space
                    dx = screen_x - mouse_x
                    dy = screen_y - win_y
                    dist = math.sqrt(dx * dx + dy * dy)
                    
                    # Click threshold (pixels)
                    threshold = 25 + pt['size'] * 15
                    
                    if dist < threshold and dist < best_dist:
                        best_dist = dist
                        best_idx = pt['index']
                except Exception:
                    continue
            
            return best_idx
        except Exception:
            return -1
    
    def update_animation(self):
        self.camera_angle = (self.camera_angle + 0.3) % 360
        self.time += 1
        self.update()
