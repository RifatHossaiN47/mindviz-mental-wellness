from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtCore import QTimer, Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random


class GardenWidget(QOpenGLWidget):
    """Stunning 3D mental wellness garden visualization.
    
    Renders a beautiful garden scene that reflects the user's emotional state:
    - Sky, weather, and lighting respond to mood/anxiety/stress
    - Flora health reflects mood
    - Water features respond to calmness
    - Atmospheric effects create immersive experience
    """
    
    def __init__(self, viz_params, metrics=None, parent=None):
        super().__init__(parent)
        self.viz = viz_params
        self.metrics_data = metrics or {}
        self.angle = 0
        self.time = 0
        self.frame_count = 0
        
        print("\n" + "=" * 60)
        print("[GARDEN] Initializing enhanced 3D visualization...")
        print(f"[GARDEN] Wellbeing: {viz_params.get('wellbeing', 'N/A')}")
        print(f"[GARDEN] Sky color: {viz_params.get('sky_color', 'N/A')}")
        print(f"[GARDEN] Rain intensity: {viz_params.get('rain_intensity', 'N/A')}")
        print(f"[GARDEN] Flower health: {viz_params.get('flower_health', 'N/A')}")
        print(f"[GARDEN] Cloud count: {viz_params.get('cloud_count', 'N/A')}")
        print("=" * 60 + "\n")
        
        # Extract all parameters with defaults
        self.sky_color = viz_params.get('sky_color', [0.4, 0.6, 0.9])
        self.horizon_color = viz_params.get('horizon_color', [0.8, 0.7, 0.5])
        self.sun_intensity = viz_params.get('sun_intensity', 0.7)
        self.sun_color = viz_params.get('sun_color', [1.0, 0.9, 0.4])
        self.time_of_day = viz_params.get('time_of_day', 0.6)
        self.cloud_darkness = viz_params.get('cloud_darkness', 0.5)
        self.cloud_count = viz_params.get('cloud_count', 5)
        self.rain_intensity = viz_params.get('rain_intensity', 0.3)
        self.lightning = viz_params.get('lightning', False)
        self.show_rainbow = viz_params.get('show_rainbow', False)
        self.fog_density = viz_params.get('fog_density', 0.2)
        self.wind_speed = viz_params.get('wind_speed', 1.0)
        self.flower_droop = viz_params.get('flower_droop', 0.5)
        self.flower_health = viz_params.get('flower_health', 0.5)
        self.flower_count = viz_params.get('flower_count', 8)
        self.flower_bloom = viz_params.get('flower_bloom', 0.5)
        self.tree_health = viz_params.get('tree_health', 0.5)
        self.leaf_density = viz_params.get('leaf_density', 0.6)
        self.leaf_fall_rate = viz_params.get('leaf_fall_rate', 0.2)
        self.grass_color = viz_params.get('grass_color', [0.25, 0.5, 0.2])
        self.water_clarity = viz_params.get('water_clarity', 0.5)
        self.water_ripple_speed = viz_params.get('water_ripple_speed', 1.0)
        self.butterfly_count = viz_params.get('butterfly_count', 3)
        self.bird_count = viz_params.get('bird_count', 2)
        self.firefly_count = viz_params.get('firefly_count', 5)
        self.god_rays = viz_params.get('god_rays', False)
        self.star_count = viz_params.get('star_count', 0)
        self.sparkle_intensity = viz_params.get('sparkle_intensity', 0.3)
        self.path_visibility = viz_params.get('path_visibility', 0.7)
        self.mountain_snow = viz_params.get('mountain_snow', 0.5)
        self.mountain_color = viz_params.get('mountain_color', [0.35, 0.38, 0.4])
        self.wellbeing = viz_params.get('wellbeing', 0.5)
        
        # Particle systems
        self.rain_drops = []
        self.butterflies = []
        self.fireflies = []
        self.birds = []
        self.falling_leaves = []
        self.sparkles = []
        self.cloud_data = []
        
        # Pre-generate stable random positions
        random.seed(42)
        self.flower_positions = []
        self._generate_flower_positions()
        self.grass_blades = []
        self._generate_grass()
        self.tree_positions = [
            (-14, 0, -8), (-9, 0, -12), (-5, 0, -10),
            (5, 0, -10), (9, 0, -12), (14, 0, -8),
            (-12, 0, -5), (12, 0, -5)
        ]
        self.bush_positions = [
            (-7, 0, 5), (-4, 0, 6), (4, 0, 6), (7, 0, 5),
            (-10, 0, 2), (10, 0, 2), (-6, 0, -3), (6, 0, -3)
        ]
        self.rock_positions = [
            (8, 0, 3), (-9, 0, 1), (3, 0, 7), (-4, 0, -2)
        ]
        random.seed()
        
        self._init_particles()
        self._init_clouds()
        
        # Animation timer (60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(16)
    
    def _generate_flower_positions(self):
        for _ in range(self.flower_count):
            for _ in range(20):
                x = random.uniform(-12, 12)
                z = random.uniform(-4, 8)
                if abs(x) < 1.2 and z > -2:
                    continue
                if (x - 6) ** 2 + (z + 1) ** 2 < 12:
                    continue
                self.flower_positions.append((x, 0, z))
                break
    
    def _generate_grass(self):
        random.seed(123)
        for _ in range(200):
            x = random.uniform(-18, 18)
            z = random.uniform(-10, 14)
            if (x - 6) ** 2 + (z + 1) ** 2 < 10:
                continue
            if abs(x) < 0.8 and z > -2:
                continue
            height = random.uniform(0.4, 1.2)
            phase = random.uniform(0, 6.28)
            self.grass_blades.append({'x': x, 'z': z, 'h': height, 'phase': phase})
        random.seed()
    
    def _init_clouds(self):
        random.seed(77)
        for i in range(self.cloud_count):
            self.cloud_data.append({
                'x': -20 + i * (40 / max(1, self.cloud_count)),
                'y': 14 + random.uniform(-1, 2),
                'z': random.uniform(-18, -8),
                'scale': random.uniform(0.8, 1.5),
                'speed': random.uniform(0.003, 0.008),
                'puffs': random.randint(4, 7)
            })
        random.seed()
    
    def _init_particles(self):
        # Rain
        for _ in range(int(self.rain_intensity * 200)):
            self.rain_drops.append({
                'x': random.uniform(-22, 22), 'y': random.uniform(5, 30),
                'z': random.uniform(-22, 22), 'speed': random.uniform(0.3, 0.6),
                'size': random.uniform(0.08, 0.15)
            })
        # Butterflies
        wing_colors = [
            [1.0, 0.4, 0.6], [0.9, 0.6, 0.2], [0.4, 0.6, 1.0],
            [0.8, 0.3, 0.9], [1.0, 0.8, 0.2], [0.3, 0.9, 0.6]
        ]
        for i in range(self.butterfly_count):
            self.butterflies.append({
                'x': random.uniform(-8, 8), 'y': random.uniform(1.5, 4),
                'z': random.uniform(-4, 5), 'angle': random.uniform(0, 360),
                'speed': random.uniform(0.015, 0.04), 'flutter': random.uniform(0, 6.28),
                'wing_color': wing_colors[i % len(wing_colors)],
                'radius': random.uniform(3, 7), 'height_var': random.uniform(0.5, 1.5)
            })
        # Birds
        for i in range(self.bird_count):
            self.birds.append({
                'x': random.uniform(-15, 15), 'y': random.uniform(10, 16),
                'z': random.uniform(-15, -5), 'angle': random.uniform(0, 360),
                'speed': random.uniform(0.02, 0.05), 'wing_phase': random.uniform(0, 6.28),
                'radius': random.uniform(8, 15)
            })
        # Fireflies
        for i in range(self.firefly_count):
            self.fireflies.append({
                'x': random.uniform(-10, 10), 'y': random.uniform(1, 5),
                'z': random.uniform(-6, 6), 'phase': random.uniform(0, 6.28),
                'brightness': random.uniform(0.5, 1.0),
                'drift_x': random.uniform(-0.02, 0.02),
                'drift_z': random.uniform(-0.02, 0.02)
            })
        # Falling leaves
        for _ in range(int(self.leaf_fall_rate * 30)):
            self.falling_leaves.append({
                'x': random.uniform(-15, 15), 'y': random.uniform(3, 12),
                'z': random.uniform(-10, 8), 'rot': random.uniform(0, 360),
                'rot_speed': random.uniform(1, 4), 'fall_speed': random.uniform(0.02, 0.06),
                'sway': random.uniform(0, 6.28),
                'color': random.choice([
                    [0.6, 0.4, 0.1], [0.7, 0.5, 0.15], [0.5, 0.3, 0.1],
                    [0.3, 0.5, 0.15], [0.4, 0.55, 0.2]
                ])
            })
        # Sparkles
        if self.sparkle_intensity > 0:
            for _ in range(int(self.sparkle_intensity * 20)):
                self.sparkles.append({
                    'x': random.uniform(-12, 12), 'y': random.uniform(0.5, 6),
                    'z': random.uniform(-8, 8), 'phase': random.uniform(0, 6.28),
                    'speed': random.uniform(0.05, 0.15)
                })
    
    # ===== OpenGL Setup =====
    
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Sun light
        ambient = [0.35 + self.sun_intensity * 0.25] * 3 + [1]
        diffuse = [c * self.sun_intensity for c in self.sun_color] + [1]
        glLightfv(GL_LIGHT0, GL_POSITION, [12, 20, -5, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 0.9, 1])
        
        # Fill light
        fill = 0.25 + self.wellbeing * 0.15
        glLightfv(GL_LIGHT1, GL_POSITION, [-15, 12, 10, 1])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [fill * 0.8, fill * 0.85, fill, 1])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [fill, fill, fill * 1.2, 1])
        
        # Fog
        if self.fog_density > 0.1:
            glEnable(GL_FOG)
            glFogi(GL_FOG_MODE, GL_EXP2)
            fog_c = [self.sky_color[i] * 0.9 + 0.1 for i in range(3)] + [1.0]
            glFogfv(GL_FOG_COLOR, fog_c)
            glFogf(GL_FOG_DENSITY, self.fog_density * 0.04)
        
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)
    
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(48, w / h if h != 0 else 1, 0.1, 120.0)
        glMatrixMode(GL_MODELVIEW)
    
    # ===== Main Render =====
    
    def paintGL(self):
        glClearColor(*self.sky_color, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        sway_x = math.sin(self.time * 0.0008) * 0.4
        sway_y = math.sin(self.time * 0.0005) * 0.15
        gluLookAt(sway_x, 5.5 + sway_y, 18, 0, 2.5, 0, 0, 1, 0)
        
        self._draw_sky_dome()
        self._draw_mountains()
        self._draw_stars()
        self._draw_sun_or_moon()
        if self.show_rainbow:
            self._draw_rainbow()
        self._draw_ground()
        self._draw_path()
        self._draw_pond()
        self._draw_trees()
        self._draw_bushes()
        self._draw_rocks()
        self._draw_flowers()
        self._draw_grass_blades()
        self._draw_clouds()
        if self.god_rays:
            self._draw_god_rays()
        self._draw_rain()
        self._draw_falling_leaves()
        self._draw_butterflies()
        self._draw_birds()
        self._draw_fireflies()
        self._draw_sparkles()
        self._draw_atmosphere_particles()
        
        # 2D text overlay using QPainter
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        if self.fog_density > 0.1:
            glDisable(GL_FOG)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        self._draw_text_overlay(painter)
        painter.end()
    
    # ===== Sky & Atmosphere =====
    
    def _draw_sky_dome(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        bands = [
            (-1.0, [c * 0.5 for c in self.sky_color]),
            (-0.3, self.sky_color),
            (0.2, [self.sky_color[i] * 0.7 + self.horizon_color[i] * 0.3 for i in range(3)]),
            (0.6, self.horizon_color),
            (1.0, [min(1.0, c * 1.1) for c in self.horizon_color])
        ]
        for i in range(len(bands) - 1):
            y1, c1 = bands[i]
            y2, c2 = bands[i + 1]
            glBegin(GL_QUADS)
            glColor3f(*c1)
            glVertex3f(-1, -y1, -0.99)
            glVertex3f(1, -y1, -0.99)
            glColor3f(*c2)
            glVertex3f(1, -y2, -0.99)
            glVertex3f(-1, -y2, -0.99)
            glEnd()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def _draw_stars(self):
        if self.star_count <= 0:
            return
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        random.seed(999)
        glPointSize(3.0)
        glBegin(GL_POINTS)
        for i in range(self.star_count):
            x = random.uniform(-25, 25)
            y = random.uniform(12, 25)
            z = random.uniform(-25, -10)
            tw = abs(math.sin(self.time * 0.003 + i * 1.7))
            glColor4f(1.0, 1.0, 0.95, tw * 0.8)
            glVertex3f(x, y, z)
        glEnd()
        glPointSize(5.0)
        glBegin(GL_POINTS)
        for i in range(self.star_count // 3):
            x = random.uniform(-20, 20)
            y = random.uniform(14, 22)
            z = random.uniform(-22, -12)
            tw = abs(math.sin(self.time * 0.002 + i * 2.3))
            glColor4f(1.0, 1.0, 0.9, tw * 0.9)
            glVertex3f(x, y, z)
        glEnd()
        random.seed()
        glPointSize(1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def _draw_sun_or_moon(self):
        glDisable(GL_LIGHTING)
        glPushMatrix()
        sun_x = 10 + math.sin(self.time * 0.0003) * 1
        sun_y = 16 + self.time_of_day * 3
        glTranslatef(sun_x, sun_y, -20)
        
        if self.wellbeing > 0.4:
            # Sun corona — small, subtle layers
            for i in range(4):
                alpha = 0.045 - i * 0.01
                glColor4f(self.sun_color[0], self.sun_color[1], self.sun_color[2] * 0.5, max(0, alpha))
                self._draw_sphere(1.8 + i * 0.4, 16, 16)
            # Sun rays — thin and dim
            for i in range(12):
                ang = 30 * i + self.time * 0.05
                glPushMatrix()
                glRotatef(ang, 0, 0, 1)
                glColor4f(1.0, 0.95, 0.5, 0.06)
                glBegin(GL_TRIANGLES)
                glVertex3f(0, 1.5, 0)
                glVertex3f(-0.12, 3.8, 0)
                glVertex3f(0.12, 3.8, 0)
                glEnd()
                glPopMatrix()
            glColor3f(*self.sun_color)
            self._draw_sphere(1.5, 24, 24)
            glColor3f(1.0, 1.0, 0.85)
            self._draw_sphere(0.8, 16, 16)
        else:
            for i in range(3):
                glColor4f(0.8, 0.85, 1.0, max(0, 0.1 - i * 0.03))
                self._draw_sphere(2.0 + i * 0.5, 20, 20)
            glColor3f(0.92, 0.92, 0.98)
            self._draw_sphere(1.2, 24, 24)
            glColor4f(0.8, 0.8, 0.88, 0.5)
            glPushMatrix()
            glTranslatef(0.3, 0.2, 1.1)
            self._draw_sphere(0.2, 10, 10)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(-0.4, -0.3, 1.0)
            self._draw_sphere(0.15, 10, 10)
            glPopMatrix()
        
        glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def _draw_rainbow(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glLineWidth(4.0)
        colors = [
            [1, 0, 0, 0.25], [1, 0.5, 0, 0.25], [1, 1, 0, 0.25],
            [0, 1, 0, 0.25], [0, 0.5, 1, 0.25], [0.3, 0, 0.8, 0.25], [0.5, 0, 1, 0.2]
        ]
        for bi, c in enumerate(colors):
            r = 18 + bi * 0.6
            glBegin(GL_LINE_STRIP)
            glColor4f(*c)
            for i in range(31):
                a = math.radians(20 + i * (140 / 30))
                glVertex3f(math.cos(a) * r, math.sin(a) * r * 0.5, -25)
            glEnd()
        glLineWidth(1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def _draw_god_rays(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        for i in range(4):
            x = -4.5 + i * 3 + math.sin(self.time * 0.001 + i) * 0.4
            a = 0.025 + math.sin(self.time * 0.002 + i * 1.5) * 0.01
            glColor4f(1.0, 0.95, 0.7, max(0, a))
            glBegin(GL_QUADS)
            glVertex3f(x - 0.2, 16, -8)
            glVertex3f(x + 0.2, 16, -8)
            glVertex3f(x + 1.2, 0, 2)
            glVertex3f(x - 1.2, 0, 2)
            glEnd()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    # ===== Terrain =====
    
    def _draw_mountains(self):
        glDisable(GL_LIGHTING)
        peaks = [
            (-20, -15, 10, 14), (-12, -5, 8, 11), (-4, 4, 12, 16),
            (3, 10, 9, 13), (8, 18, 11, 15), (16, 22, 7, 10)
        ]
        for x1, x2, h1, h2 in peaks:
            pk = (x1 + x2) / 2
            h = max(h1, h2)
            mc = self.mountain_color
            glBegin(GL_TRIANGLES)
            glColor3f(mc[0], mc[1], mc[2])
            glVertex3f(x1, 0, -22)
            glVertex3f(x2, 0, -22)
            glColor3f(min(1, mc[0] + 0.15), min(1, mc[1] + 0.15), min(1, mc[2] + 0.15))
            glVertex3f(pk, h, -22)
            glEnd()
            if self.mountain_snow > 0.2:
                sw = (x2 - x1) * 0.25
                sl = h * (1 - self.mountain_snow * 0.3)
                glColor4f(0.95, 0.95, 1.0, self.mountain_snow)
                glBegin(GL_TRIANGLES)
                glVertex3f(pk - sw, sl, -21.9)
                glVertex3f(pk + sw, sl, -21.9)
                glVertex3f(pk, h + 0.1, -21.9)
                glEnd()
        glEnable(GL_LIGHTING)
    
    def _draw_ground(self):
        glBegin(GL_QUADS)
        tile = 3
        random.seed(55)
        for x in range(-7, 7):
            for z in range(-5, 6):
                fx, fz = x * tile, z * tile
                cx, cz = fx + tile / 2, fz + tile / 2
                if (cx - 6) ** 2 + (cz + 1) ** 2 < 14:
                    continue
                v = random.uniform(-0.03, 0.03)
                dist = math.sqrt(fx * fx + fz * fz) / 25
                fade = max(0.7, 1.0 - dist * 0.3)
                r = max(0, min(1, (self.grass_color[0] + v) * fade))
                g = max(0, min(1, (self.grass_color[1] + v) * fade))
                b = max(0, min(1, (self.grass_color[2] + v * 0.5) * fade))
                glColor3f(r, g, b)
                glNormal3f(0, 1, 0)
                glVertex3f(fx, 0, fz)
                glVertex3f(fx + tile, 0, fz)
                glVertex3f(fx + tile, 0, fz + tile)
                glVertex3f(fx, 0, fz + tile)
        random.seed()
        glEnd()
    
    def _draw_path(self):
        glDisable(GL_LIGHTING)
        pa = self.path_visibility
        random.seed(200)
        for i in range(18):
            t = i / 18
            zp = -4 + t * 16
            xp = math.sin(t * 3.14) * 1.5
            glPushMatrix()
            glTranslatef(xp, 0.02, zp)
            glRotatef(-90, 1, 0, 0)
            sv = random.uniform(-0.05, 0.05)
            glColor4f(0.6 + sv, 0.58 + sv, 0.52 + sv, pa * 0.8)
            quad = gluNewQuadric()
            sz = 0.5 + random.uniform(-0.1, 0.15)
            gluDisk(quad, 0, sz, 12, 1)
            gluDeleteQuadric(quad)
            glColor4f(0.5, 0.48, 0.42, pa * 0.5)
            quad = gluNewQuadric()
            gluDisk(quad, sz - 0.1, sz, 12, 1)
            gluDeleteQuadric(quad)
            glPopMatrix()
        random.seed()
        glEnable(GL_LIGHTING)
    
    def _draw_pond(self):
        px, pz, pr = 6, -1, 3.2
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        # Bottom
        glPushMatrix()
        glTranslatef(px, -0.1, pz)
        glRotatef(-90, 1, 0, 0)
        glColor4f(0.1, 0.15, 0.2, 0.9)
        q = gluNewQuadric()
        gluDisk(q, 0, pr + 0.3, 32, 1)
        gluDeleteQuadric(q)
        glPopMatrix()
        # Water surface
        glPushMatrix()
        glTranslatef(px, 0.05, pz)
        glRotatef(-90, 1, 0, 0)
        wr = 0.15 + (1 - self.water_clarity) * 0.2
        wg = 0.3 + self.water_clarity * 0.2
        wb = 0.45 + self.water_clarity * 0.3
        for ring in range(8):
            ri = ring * pr / 8
            ro = (ring + 1) * pr / 8
            rip = math.sin(self.time * 0.003 * self.water_ripple_speed + ring * 0.8) * 0.03
            alpha = 0.5 + self.water_clarity * 0.3 - ring * 0.02
            glColor4f(wr, wg + rip, wb + rip, alpha)
            glBegin(GL_QUAD_STRIP)
            for s in range(33):
                a = s * (2 * math.pi / 32)
                w = math.sin(a * 3 + self.time * 0.004) * 0.01
                glVertex3f(math.cos(a) * ri, math.sin(a) * ri + w, 0)
                glVertex3f(math.cos(a) * ro, math.sin(a) * ro + w, 0)
            glEnd()
        glPopMatrix()
        # Sky reflection
        glPushMatrix()
        glTranslatef(px + 0.5, 0.08, pz - 0.5)
        glRotatef(-90, 1, 0, 0)
        ra = self.water_clarity * 0.15
        glColor4f(self.sky_color[0], self.sky_color[1], self.sky_color[2], ra)
        q = gluNewQuadric()
        gluDisk(q, 0, pr * 0.6, 20, 1)
        gluDeleteQuadric(q)
        glPopMatrix()
        # Lily pads
        if self.water_clarity > 0.4:
            for lx, lz in [(px - 1, pz + 0.8), (px + 1.2, pz - 0.5), (px - 0.3, pz - 1.2)]:
                glPushMatrix()
                glTranslatef(lx, 0.1, lz)
                glRotatef(-90, 1, 0, 0)
                glColor4f(0.15, 0.55, 0.2, 0.85)
                q = gluNewQuadric()
                gluDisk(q, 0, 0.4, 16, 1)
                gluDeleteQuadric(q)
                glPopMatrix()
        # Border stones
        for i in range(16):
            a = (2 * math.pi / 16) * i
            glPushMatrix()
            glTranslatef(px + math.cos(a) * (pr + 0.2), 0, pz + math.sin(a) * (pr + 0.2))
            glColor3f(0.45, 0.42, 0.38)
            self._draw_sphere(0.25, 8, 8)
            glPopMatrix()
        glEnable(GL_LIGHTING)
    
    # ===== Flora =====
    
    def _draw_trees(self):
        for idx, (x, y, z) in enumerate(self.tree_positions):
            glPushMatrix()
            glTranslatef(x, y, z)
            tr = 0.3 + (idx % 3) * 0.05
            th = 3.5 + (idx % 4) * 0.5
            glColor3f(0.35, 0.22, 0.1)
            self._draw_tapered_cylinder(tr, tr * 0.6, th, 10)
            for b in range(3):
                glPushMatrix()
                glTranslatef(0, th * (0.5 + b * 0.15), 0)
                glRotatef(120 * b + idx * 30, 0, 1, 0)
                glRotatef(35 + b * 5, 0, 0, 1)
                glColor3f(0.3, 0.2, 0.1)
                self._draw_tapered_cylinder(tr * 0.3, tr * 0.15, 1.5, 6)
                glPopMatrix()
            glTranslatef(0, th, 0)
            if self.tree_health > 0.6:
                lc = [0.15, 0.5 + self.tree_health * 0.2, 0.12]
            elif self.tree_health > 0.3:
                lc = [0.35, 0.4, 0.12]
            else:
                lc = [0.45, 0.3, 0.1]
            offsets = [
                (0, 0, 0, 2.0), (0.8, 0.6, 0.4, 1.6), (-0.7, 0.5, -0.3, 1.5),
                (0.3, 1.0, -0.5, 1.3), (-0.4, 0.8, 0.5, 1.4), (0, 1.3, 0, 1.1)
            ]
            for ox, oy, oz, sz in offsets[:int(2 + self.leaf_density * 4)]:
                glPushMatrix()
                glTranslatef(ox, oy, oz)
                glColor3f(lc[0], lc[1], lc[2])
                self._draw_sphere(sz, 14, 14)
                glPopMatrix()
            glPopMatrix()
    
    def _draw_bushes(self):
        for idx, (x, y, z) in enumerate(self.bush_positions):
            glPushMatrix()
            glTranslatef(x, y, z)
            bc = [self.grass_color[0] * 0.7, self.grass_color[1] * 0.9 + 0.05, self.grass_color[2] * 0.8]
            for ox, oy, oz, sz in [(0, 0, 0, 0.7), (0.4, 0.1, 0, 0.6), (-0.35, 0.05, 0.2, 0.55),
                                    (0, 0.3, -0.1, 0.5), (0.2, -0.1, 0.3, 0.45)]:
                glPushMatrix()
                glTranslatef(ox, oy + sz * 0.5, oz)
                v = (idx * 0.02) % 0.06
                glColor3f(bc[0] + v, bc[1] + v, bc[2])
                self._draw_sphere(sz, 10, 10)
                glPopMatrix()
            if self.flower_health > 0.5 and idx % 2 == 0:
                for b in range(3):
                    glPushMatrix()
                    glTranslatef(math.sin(b * 2.1) * 0.3, 0.5 + b * 0.15, math.cos(b * 1.7) * 0.2)
                    glColor3f(0.8, 0.15, 0.15)
                    self._draw_sphere(0.08, 6, 6)
                    glPopMatrix()
            glPopMatrix()
    
    def _draw_rocks(self):
        for idx, (x, y, z) in enumerate(self.rock_positions):
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor3f(0.5, 0.48, 0.44)
            glScalef(1.0, 0.5, 0.8)
            self._draw_sphere(0.6 + idx * 0.1, 10, 10)
            glPushMatrix()
            glTranslatef(0.5, 0, 0.3)
            glColor3f(0.45, 0.43, 0.4)
            self._draw_sphere(0.3, 8, 8)
            glPopMatrix()
            glPopMatrix()
    
    def _draw_flowers(self):
        healthy_colors = [
            [1.0, 0.3, 0.5], [1.0, 0.85, 0.1], [0.7, 0.3, 0.85], [1.0, 0.5, 0.15],
            [0.45, 0.7, 1.0], [1.0, 0.4, 0.4], [0.85, 0.5, 0.85], [1.0, 0.6, 0.7]
        ]
        for idx, (x, y, z) in enumerate(self.flower_positions):
            glPushMatrix()
            glTranslatef(x, y, z)
            droop = self.flower_droop * 25
            ws = math.sin(self.time * 0.003 + idx * 0.7) * self.wind_speed * 3
            glRotatef(droop + ws, 0, 0, 1)
            glRotatef(ws * 0.3, 1, 0, 0)
            sh = 2.0 + (idx % 3) * 0.5
            glColor3f(0.18, 0.55, 0.15)
            for seg in range(8):
                h = seg * sh / 8
                curve = math.sin(h * 0.5 + self.time * 0.002) * 0.05
                glPushMatrix()
                glTranslatef(curve, h, 0)
                self._draw_cylinder(0.04, sh / 8, 6)
                glPopMatrix()
            for lh in [sh * 0.3, sh * 0.6]:
                glPushMatrix()
                glTranslatef(0, lh, 0)
                glRotatef(45, 0, 1, 0)
                glRotatef(30, 0, 0, 1)
                glColor3f(0.15, 0.5, 0.12)
                glScalef(1.0, 0.3, 0.5)
                self._draw_sphere(0.2, 6, 6)
                glPopMatrix()
            glTranslatef(0, sh, 0)
            if self.flower_health < 0.25:
                color = [0.45, 0.35, 0.25]
            elif self.flower_health < 0.5:
                color = [0.7, 0.5, 0.25]
            else:
                color = healthy_colors[idx % len(healthy_colors)]
            pc = 6 + (idx % 4) * 2
            bs = 0.4 + self.flower_bloom * 0.8
            for p in range(pc):
                pa = (360 / pc) * p
                glPushMatrix()
                glRotatef(pa, 0, 1, 0)
                glTranslatef(0.25 * bs, 0, 0)
                glRotatef(50 + (1 - self.flower_bloom) * 30, 0, 0, 1)
                pt = [min(1.0, c * 1.2) for c in color]
                glBegin(GL_TRIANGLE_FAN)
                glColor3f(*color)
                glVertex3f(0, 0, 0)
                for pi in range(11):
                    a = (pi / 10.0) * math.pi
                    if pi > 5:
                        glColor3f(*pt)
                    glVertex3f(math.cos(a) * 0.2 * bs, math.sin(a) * 0.4 * bs, 0)
                glEnd()
                glPopMatrix()
            cc = [min(1.0, c * 1.5 + 0.2) for c in color]
            glColor3f(*cc)
            self._draw_sphere(0.15 * bs, 10, 10)
            if self.flower_health > 0.75:
                glDisable(GL_LIGHTING)
                glColor4f(color[0], color[1], color[2], 0.15)
                self._draw_sphere(0.35 * bs, 10, 10)
                glEnable(GL_LIGHTING)
            glPopMatrix()
    
    def _draw_grass_blades(self):
        glDisable(GL_LIGHTING)
        gl_ = [min(1.0, c * 1.15) for c in self.grass_color]
        gd_ = [max(0, c * 0.85) for c in self.grass_color]
        glLineWidth(1.5)
        glBegin(GL_LINES)
        for bl in self.grass_blades:
            sw = math.sin(self.time * 0.003 + bl['phase']) * self.wind_speed * 0.12
            swz = math.cos(self.time * 0.004 + bl['phase'] * 0.7) * self.wind_speed * 0.06
            t = (math.sin(bl['phase']) + 1) * 0.5
            r = gd_[0] + (gl_[0] - gd_[0]) * t
            g = gd_[1] + (gl_[1] - gd_[1]) * t
            b = gd_[2] + (gl_[2] - gd_[2]) * t
            glColor3f(r, g, b)
            glVertex3f(bl['x'], 0, bl['z'])
            glColor3f(min(1, r + 0.05), min(1, g + 0.1), b)
            glVertex3f(bl['x'] + sw, bl['h'], bl['z'] + swz)
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    # ===== Weather =====
    
    def _draw_clouds(self):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        for cl in self.cloud_data:
            glPushMatrix()
            x = cl['x'] + math.sin(self.time * cl['speed']) * 5
            glTranslatef(x, cl['y'], cl['z'])
            glScalef(cl['scale'], cl['scale'] * 0.5, cl['scale'] * 0.6)
            brt = max(0.35, 1.0 - self.cloud_darkness * 0.8)
            alpha = 0.55 + self.cloud_darkness * 0.2
            puffs = [
                (0, 0, 0, 1.8), (1.5, 0.2, 0.2, 1.5), (-1.3, 0.1, -0.2, 1.4),
                (0.6, 0.5, 0.1, 1.2), (-0.5, 0.4, 0.3, 1.3),
                (0.3, -0.3, -0.1, 1.1), (-0.8, -0.2, 0.2, 1.0)
            ]
            for px, py, pz, ps in puffs[:cl['puffs']]:
                glPushMatrix()
                glTranslatef(px, py, pz)
                bv = brt + py * 0.1
                glColor4f(bv, bv, min(1, bv + 0.05), alpha)
                self._draw_sphere(ps, 12, 12)
                glPopMatrix()
            if self.cloud_darkness > 0.4:
                glPushMatrix()
                glTranslatef(0, -0.8, 0)
                dv = brt * 0.6
                glColor4f(dv, dv, dv, alpha * 0.7)
                self._draw_sphere(1.5, 10, 10)
                glPopMatrix()
            glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def _draw_rain(self):
        if self.rain_intensity < 0.05:
            return
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glLineWidth(1.5)
        alpha = 0.3 + self.rain_intensity * 0.3
        wx = self.wind_speed * 0.15
        glBegin(GL_LINES)
        for d in self.rain_drops:
            glColor4f(0.55, 0.65, 0.85, alpha)
            glVertex3f(d['x'], d['y'], d['z'])
            glVertex3f(d['x'] + wx * 0.3, d['y'] - 1.0 - self.rain_intensity * 0.5, d['z'])
        glEnd()
        glPointSize(3.0)
        glBegin(GL_POINTS)
        for d in self.rain_drops:
            if d['y'] < 0.5:
                glColor4f(0.65, 0.75, 0.9, (0.5 - d['y']) * 0.6)
                glVertex3f(d['x'], 0.05, d['z'])
        glEnd()
        glPointSize(1.0)
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    def _draw_falling_leaves(self):
        if not self.falling_leaves:
            return
        glDisable(GL_LIGHTING)
        for lf in self.falling_leaves:
            glPushMatrix()
            glTranslatef(lf['x'], lf['y'], lf['z'])
            glRotatef(lf['rot'], 0, 1, 0)
            glRotatef(lf['rot'] * 0.5, 1, 0, 0)
            glColor4f(lf['color'][0], lf['color'][1], lf['color'][2], 0.8)
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0)
            glVertex3f(0.08, 0.15, 0)
            glVertex3f(-0.08, 0.12, 0)
            glEnd()
            glPopMatrix()
        glEnable(GL_LIGHTING)
    
    # ===== Creatures =====
    
    def _draw_butterflies(self):
        if not self.butterflies:
            return
        glDisable(GL_LIGHTING)
        for bf in self.butterflies:
            glPushMatrix()
            glTranslatef(bf['x'], bf['y'], bf['z'])
            glRotatef(bf['angle'], 0, 1, 0)
            fl = math.sin(bf['flutter']) * 30
            c = bf['wing_color']
            glColor3f(0.15, 0.1, 0.05)
            glPushMatrix()
            glScalef(0.05, 0.1, 0.05)
            self._draw_sphere(1.0, 6, 6)
            glPopMatrix()
            for side in (-1, 1):
                glPushMatrix()
                glRotatef(fl * side, 0, 0, 1)
                glColor4f(c[0], c[1], c[2], 0.85)
                glBegin(GL_TRIANGLE_FAN)
                glVertex3f(0, 0, 0)
                glVertex3f(side * 0.35, 0.2, 0)
                glColor4f(c[0] * 0.7, c[1] * 0.7, c[2] * 0.7, 0.85)
                glVertex3f(side * 0.4, 0, 0)
                glVertex3f(side * 0.3, -0.15, 0)
                glEnd()
                glColor4f(1, 1, 1, 0.6)
                glPushMatrix()
                glTranslatef(side * 0.25, 0.05, 0.01)
                self._draw_sphere(0.04, 4, 4)
                glPopMatrix()
                glPopMatrix()
            glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def _draw_birds(self):
        if not self.birds:
            return
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        for bird in self.birds:
            glPushMatrix()
            glTranslatef(bird['x'], bird['y'], bird['z'])
            glRotatef(math.degrees(bird['angle']), 0, 1, 0)
            w = math.sin(bird['wing_phase']) * 15
            glColor4f(0.15, 0.12, 0.1, 0.7)
            glBegin(GL_LINE_STRIP)
            glVertex3f(-0.5, math.sin(math.radians(w)) * 0.2, 0)
            glVertex3f(-0.15, 0, 0)
            glVertex3f(0, 0.05, 0)
            glVertex3f(0.15, 0, 0)
            glVertex3f(0.5, math.sin(math.radians(w)) * 0.2, 0)
            glEnd()
            glPopMatrix()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    def _draw_fireflies(self):
        if not self.fireflies:
            return
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        for ff in self.fireflies:
            pulse = abs(math.sin(self.time * 0.002 + ff['phase']))
            br = ff['brightness'] * pulse
            if br < 0.1:
                continue
            glPushMatrix()
            glTranslatef(ff['x'], ff['y'], ff['z'])
            glColor4f(1.0, 0.95, 0.3, br * 0.15)
            self._draw_sphere(0.4, 8, 8)
            glColor4f(1.0, 0.95, 0.4, br * 0.3)
            self._draw_sphere(0.2, 8, 8)
            glColor4f(1.0, 1.0, 0.6, br * 0.9)
            self._draw_sphere(0.06, 6, 6)
            glPopMatrix()
        glEnable(GL_LIGHTING)
    
    # ===== Effects =====
    
    def _draw_sparkles(self):
        if not self.sparkles:
            return
        glDisable(GL_LIGHTING)
        glPointSize(4.0)
        glBegin(GL_POINTS)
        for sp in self.sparkles:
            br = abs(math.sin(self.time * sp['speed'] + sp['phase']))
            if br > 0.5:
                glColor4f(1, 1, 0.9, (br - 0.5) * 1.5)
                glVertex3f(sp['x'], sp['y'] + math.sin(self.time * 0.002 + sp['phase']) * 0.3, sp['z'])
        glEnd()
        glPointSize(1.0)
        glEnable(GL_LIGHTING)
    
    def _draw_atmosphere_particles(self):
        glDisable(GL_LIGHTING)
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for i in range(40):
            x = math.sin(self.time * 0.0007 + i * 1.1) * 12
            y = 1.5 + math.sin(self.time * 0.0005 + i * 0.7) * 3
            z = math.cos(self.time * 0.0009 + i * 0.9) * 10
            a = 0.3 + math.sin(self.time * 0.002 + i) * 0.15
            if self.wellbeing > 0.5:
                glColor4f(1, 1, 0.9, a)
            else:
                glColor4f(0.7, 0.7, 0.75, a * 0.7)
            glVertex3f(x, y, z)
        glEnd()
        glPointSize(1.0)
        glEnable(GL_LIGHTING)
    
    # ===== Utility =====
    
    def _draw_sphere(self, radius, slices, stacks):
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_SMOOTH)
        gluSphere(q, radius, slices, stacks)
        gluDeleteQuadric(q)
    
    def _draw_cylinder(self, radius, height, slices):
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_SMOOTH)
        gluCylinder(q, radius, radius, height, slices, 1)
        gluDeleteQuadric(q)
    
    def _draw_tapered_cylinder(self, r_base, r_top, height, slices):
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_SMOOTH)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        gluCylinder(q, r_base, r_top, height, slices, 1)
        glPopMatrix()
        gluDeleteQuadric(q)
    
    def _draw_text_overlay(self, painter):
        """Draw semi-transparent overlay showing emotional state information"""
        w, h = self.width(), self.height()
        
        analysis = self.metrics_data.get('analysis', {})
        anxiety = self.metrics_data.get('anxiety', 0.5)
        mood = self.metrics_data.get('mood', 0.5)
        stress = self.metrics_data.get('stress', 0.5)
        
        # --- Top-left: Wellbeing panel ---
        panel_w, panel_h = 250, 178
        margin = 12
        
        # Glass background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 120))
        painter.drawRoundedRect(margin, margin, panel_w, panel_h, 10, 10)
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(margin, margin, panel_w, panel_h, 10, 10)
        
        # Wellbeing header
        painter.setPen(QColor(180, 180, 180))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(margin + 12, margin + 18, "OVERALL WELLBEING")
        
        # Wellbeing score
        wb_color = self._get_wellbeing_qcolor()
        painter.setPen(wb_color)
        painter.setFont(QFont("Arial", 28, QFont.Bold))
        painter.drawText(margin + 12, margin + 55, f"{int(self.wellbeing * 100)}%")
        
        # Wellbeing bar
        bar_x, bar_y = margin + 12, margin + 62
        bar_w = panel_w - 24
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(50, 50, 50))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, 5, 2, 2)
        painter.setBrush(wb_color)
        painter.drawRoundedRect(bar_x, bar_y, int(bar_w * self.wellbeing), 5, 2, 2)
        
        # Metric rows
        metrics_list = [
            ("Anxiety", anxiety, QColor(239, 83, 80)),
            ("Mood", mood, QColor(102, 187, 106)),
            ("Stress", stress, QColor(255, 167, 38))
        ]
        y = bar_y + 18
        for name, val, color in metrics_list:
            painter.setPen(QColor(170, 170, 170))
            painter.setFont(QFont("Arial", 9))
            painter.drawText(bar_x, y, name)
            painter.setPen(color)
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.drawText(bar_x + 55, y, f"{int(val * 100)}%")
            mini_x = bar_x + 95
            mini_w = bar_w - 95
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(50, 50, 50))
            painter.drawRoundedRect(mini_x, y - 8, mini_w, 4, 2, 2)
            painter.setBrush(color)
            painter.drawRoundedRect(mini_x, y - 8, int(mini_w * val), 4, 2, 2)
            y += 22
        
        # --- Bottom: Garden description ---
        garden_desc = analysis.get('garden_description', '') if isinstance(analysis, dict) else ''
        primary = analysis.get('primary_emotion', '') if isinstance(analysis, dict) else ''
        if garden_desc or primary:
            line_count = 1
            if garden_desc:
                line_count += 1
            if primary:
                line_count += 1
            desc_h = 20 + line_count * 18
            desc_y = h - desc_h - margin
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 100))
            painter.drawRoundedRect(margin, desc_y, w - margin * 2, desc_h, 8, 8)
            cy = desc_y + 18
            if primary:
                painter.setPen(QColor(170, 200, 255))
                painter.setFont(QFont("Arial", 9, QFont.Bold))
                painter.drawText(margin + 10, cy, f"Feeling: {primary}")
                cy += 18
            if garden_desc:
                display = garden_desc if len(garden_desc) <= 100 else garden_desc[:97] + "..."
                painter.setPen(QColor(200, 220, 200))
                painter.setFont(QFont("Arial", 9))
                painter.drawText(margin + 10, cy, display)
    
    def _get_wellbeing_qcolor(self):
        if self.wellbeing > 0.7:
            return QColor(102, 187, 106)
        elif self.wellbeing > 0.5:
            return QColor(255, 238, 88)
        elif self.wellbeing > 0.3:
            return QColor(255, 167, 38)
        return QColor(239, 83, 80)
    
    def _update_animation(self):
        self.time += 1
        self.frame_count += 1
        for d in self.rain_drops:
            d['y'] -= d['speed']
            d['x'] += self.wind_speed * 0.02
            if d['y'] < 0:
                d['y'] = random.uniform(18, 28)
                d['x'] = random.uniform(-20, 20)
                d['z'] = random.uniform(-20, 20)
        for bf in self.butterflies:
            bf['angle'] += bf['speed'] * 3
            bf['flutter'] += 0.2
            bf['x'] = math.cos(math.radians(bf['angle'])) * bf['radius']
            bf['z'] = math.sin(math.radians(bf['angle'])) * bf['radius'] * 0.6
            bf['y'] = 2 + math.sin(bf['flutter'] * 0.2) * bf['height_var']
        for bird in self.birds:
            bird['angle'] += bird['speed']
            bird['wing_phase'] += 0.12
            bird['x'] = math.cos(bird['angle']) * bird['radius']
            bird['z'] = math.sin(bird['angle']) * bird['radius'] * 0.5 - 5
            bird['y'] = 11 + math.sin(bird['angle'] * 2) * 1.5
        for ff in self.fireflies:
            ff['phase'] += 0.04
            ff['x'] += ff['drift_x'] + math.sin(self.time * 0.002) * 0.005
            ff['z'] += ff['drift_z'] + math.cos(self.time * 0.003) * 0.005
            if abs(ff['x']) > 12:
                ff['drift_x'] *= -1
            if abs(ff['z']) > 8:
                ff['drift_z'] *= -1
        for lf in self.falling_leaves:
            lf['y'] -= lf['fall_speed']
            lf['rot'] += lf['rot_speed']
            lf['x'] += math.sin(self.time * 0.003 + lf['sway']) * 0.02
            if lf['y'] < 0:
                lf['y'] = random.uniform(6, 12)
                lf['x'] = random.uniform(-14, 14)
                lf['z'] = random.uniform(-9, 7)
        self.update()
