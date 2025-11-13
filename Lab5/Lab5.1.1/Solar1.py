import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimer, Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from math import sin, cos, pi


def draw_sphere(radius, slices, stacks):
    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)


def load_texture(file_path):
    # Safe texture loader: returns texture id (creates 2x2 black if missing/error)
    if not os.path.exists(file_path):
        print(f"Ошибка: файл текстуры не найден: {file_path}")
        # create fallback 2x2 black texture
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        black_texture = bytes([0, 0, 0, 255]) * 4
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 2, 2, 0, GL_RGBA, GL_UNSIGNED_BYTE, black_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        return texture_id

    try:
        image = Image.open(file_path).convert("RGBA")
        width, height = image.size
        image_data = image.tobytes("raw", "RGBA", 0, -1)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        return texture_id
    except Exception as e:
        print(f"Ошибка загрузки текстуры {file_path}: {e}")
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        black_texture = bytes([0, 0, 0, 255]) * 4
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 2, 2, 0, GL_RGBA, GL_UNSIGNED_BYTE, black_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        return texture_id


def load_texture_skybox(filename):
    # Expects a 4x1 (or similar) layout where each face is side_length x side_length.
    if not os.path.exists(filename):
        print(f"Ошибка: файл skybox не найден: {filename} — используем цветные стороны.")
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
        textures = []
        for c in colors:
            tid = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tid)
            data = bytes(c + (255,)) * 4
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 2, 2, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            textures.append(tid)
        return textures

    try:
        image = Image.open(filename).convert("RGBA")
        width, height = image.size
        # assume 4x1 arrangement or 6 faces in a row
        side_length = width // 4 if width // 4 > 0 else min(width, height)
        textures = []
        # If it's 6-in-row use side_length = width // 6, but try both heuristics
        if width >= height and width // height >= 4:
            # try 6 faces across if width//height >= 4 but not necessarily 6; safe to try 6
            possible = []
            if width // 6 >= 1:
                possible.append(6)
            if width // 4 >= 1:
                possible.append(4)
            n = 6 if 6 in possible else 4
            side_length = width // n
            faces = n
        else:
            faces = 6
            side_length = min(width, height) // faces if min(width, height) // faces >= 1 else min(width, height)

        # fallback: if side_length is too small, just create colored faces
        if side_length < 1:
            return load_texture_skybox(None)

        # Try to extract 6 faces by scanning across
        for i in range(6):
            left = side_length * i
            top = 0
            right = left + side_length
            bottom = top + side_length
            # clamp
            if right > width:
                right = width
                left = max(0, right - side_length)
            texture_image = image.crop((left, top, right, bottom)).resize((side_length, side_length))
            texture_data = texture_image.tobytes("raw", "RGBA", 0, -1)
            tid = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tid)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, side_length, side_length, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            textures.append(tid)
        return textures
    except Exception as e:
        print(f"Ошибка загрузки skybox {filename}: {e}")
        return load_texture_skybox(None)


class SolarSystemWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sun_angle = 7.25
        self.earth_angle = 23.5
        self.moon_angle = 0.0
        self.camera_distance = 10.0
        self.camera_angle_x = 0.0
        self.camera_angle_y = 0.0
        self.last_mouse_pos = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        self.sun_texture = 0
        self.earth_texture = 0
        self.moon_texture = 0
        self.skybox_textures = []
        self.skybox_size = 50.0

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glShadeModel(GL_SMOOTH)

        # Projection will be set in resizeGL as well
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # load textures (relative folder "textures")
        base_path = os.path.join(os.path.dirname(__file__), "textures")
        self.sun_texture = load_texture(os.path.join(base_path, "sun.jpg"))
        self.earth_texture = load_texture(os.path.join(base_path, "earth.jpg"))
        self.moon_texture = load_texture(os.path.join(base_path, "moon.jpg"))
        self.skybox_textures = load_texture_skybox(os.path.join(base_path, "skybox.jpg"))

        for tid in self.skybox_textures:
            glBindTexture(GL_TEXTURE_2D, tid)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # Light params
        light_position = [0.0, 0.0, 0.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.05, 0.05, 0.05, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    def resizeGL(self, w, h):
        if h == 0:
            h = 1
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h, 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # skybox (draw first, with depth test off)
        self.draw_skybox()

        # camera transforms
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_angle_x, 1.0, 0.0, 0.0)
        glRotatef(self.camera_angle_y, 0.0, 1.0, 0.0)

        # Sun
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.sun_texture)
        glColor3f(1.0, 1.0, 1.0)
        draw_sphere(1.0, 50, 50)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        # Earth (orbit around sun)
        glPushMatrix()
        glRotatef(self.sun_angle, 0.0, 1.0, 0.0)
        glTranslatef(5.0, 0.0, 0.0)
        glRotatef(self.earth_angle, 0.0, 1.0, 0.0)

        # material for earth
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.earth_texture)
        draw_sphere(0.5, 50, 50)

        # Moon (orbit around earth)
        glPushMatrix()
        glRotatef(self.moon_angle, 0.0, 1.0, 0.0)
        glTranslatef(1.0, 0.0, 0.0)
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.3, 0.3, 0.3, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 20.0)
        glBindTexture(GL_TEXTURE_2D, self.moon_texture)
        draw_sphere(0.2, 50, 50)
        glPopMatrix()  # moon
        glPopMatrix()  # earth

    def draw_skybox(self):
        # draw a large cube centered on camera using the skybox textures
        glPushAttrib(GL_ENABLE_BIT)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_angle_x, 1, 0, 0)
        glRotatef(self.camera_angle_y, 0, 1, 0)

        s = self.skybox_size
        # faces: 0..5 assuming textures in that order
        faces = [
            (-s, -s, -s,  s, -s, -s,  s,  s, -s, -s,  s, -s),  # front
            (-s, -s,  s,  s, -s,  s,  s,  s,  s, -s,  s,  s),  # back
            (-s,  s, -s, -s,  s,  s,  s,  s,  s,  s,  s, -s),  # top
            (-s, -s, -s,  s, -s, -s,  s, -s,  s, -s, -s,  s),  # bottom
            (-s, -s, -s, -s, -s,  s, -s,  s,  s, -s,  s, -s),  # right
            ( s, -s, -s,  s, -s,  s,  s,  s,  s,  s,  s, -s),  # left
        ]

        for i, coords in enumerate(faces):
            if i >= len(self.skybox_textures):
                continue
            glBindTexture(GL_TEXTURE_2D, self.skybox_textures[i])
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex3f(coords[0], coords[1], coords[2])
            glTexCoord2f(1, 0); glVertex3f(coords[3], coords[4], coords[5])
            glTexCoord2f(1, 1); glVertex3f(coords[6], coords[7], coords[8])
            glTexCoord2f(0, 1); glVertex3f(coords[9], coords[10], coords[11])
            glEnd()

        glPopAttrib()

    def update_animation(self):
        self.sun_angle += 0.1
        self.earth_angle += 1.0
        self.moon_angle += 2.0
        self.update()

    # mouse handling: left-drag to rotate, wheel to zoom
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.camera_angle_y += delta.x() / 5.0
            self.camera_angle_x += delta.y() / 5.0
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None

    def wheelEvent(self, event):
        # Qt angleDelta is in eighths of a degree; normalize
        delta = event.angleDelta().y() / 120.0
        self.camera_distance = max(2.0, self.camera_distance - delta)
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Sun, Earth and Moon")
        self.central_widget = SolarSystemWidget(self)
        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())