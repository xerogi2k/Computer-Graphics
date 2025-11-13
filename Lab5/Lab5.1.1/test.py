import sys
import os
from math import sin, cos, pi
from PIL import Image

# УБЕРИ ВСЕ СТРОКИ С ПУТЯМИ К ПЛАГИНАМ!
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''  # УДАЛИ ЭТУ ХУЙНЮ!

from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
from PyQt5.QtCore import QTimer, Qt
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class SolarSystemWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sun_angle = 7.25
        self.earth_angle = 23.5
        self.moon_angle = 0
        self.camera_distance = 10.0
        self.camera_angle_x = 0.0
        self.camera_angle_y = 0.0
        self.last_mouse_pos = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

        self.sun_texture = None
        self.earth_texture = None
        self.moon_texture = None
        self.skybox_textures = None

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

        # Создаем простые текстуры вместо загрузки файлов
        self.create_default_textures()

        # Настройка освещения
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        light_position = [0.0, 0.0, 0.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        light_diffuse = [1.0, 1.0, 1.0, 1.0]
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

    def create_default_textures(self):
        """Создаем простые текстуры если файлы не найдены"""
        # Солнце - желтая текстура
        self.sun_texture = self.create_color_texture(255, 255, 0)
        # Земля - синяя текстура
        self.earth_texture = self.create_color_texture(0, 0, 255)
        # Луна - серая текстура
        self.moon_texture = self.create_color_texture(128, 128, 128)
        # Skybox - разноцветные стороны
        self.skybox_textures = [
            self.create_color_texture(255, 0, 0),  # красный
            self.create_color_texture(0, 255, 0),  # зеленый
            self.create_color_texture(0, 0, 255),  # синий
            self.create_color_texture(255, 255, 0),  # желтый
            self.create_color_texture(255, 0, 255),  # пурпурный
            self.create_color_texture(0, 255, 255),  # голубой
        ]

    def create_color_texture(self, r, g, b, size=64):
        """Создает одноцветную текстуру"""
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Создаем данные текстуры
        texture_data = bytes([r, g, b, 255]) * (size * size)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        return texture_id

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Камера
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_angle_x, 1.0, 0.0, 0.0)
        glRotatef(self.camera_angle_y, 0.0, 1.0, 0.0)

        # Солнце
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.sun_texture)
        glColor3f(1.0, 1.0, 0.0)  # желтый
        self.draw_sphere(1.0, 32, 32)

        # Земля
        glPushMatrix()
        glRotatef(self.sun_angle, 0.0, 1.0, 0.0)
        glTranslatef(3.0, 0.0, 0.0)
        glRotatef(self.earth_angle, 0.0, 1.0, 0.0)

        glBindTexture(GL_TEXTURE_2D, self.earth_texture)
        glColor3f(0.0, 0.0, 1.0)  # синий
        self.draw_sphere(0.4, 32, 32)

        # Луна
        glPushMatrix()
        glRotatef(self.moon_angle, 0.0, 1.0, 0.0)
        glTranslatef(1.0, 0.0, 0.0)

        glBindTexture(GL_TEXTURE_2D, self.moon_texture)
        glColor3f(0.5, 0.5, 0.5)  # серый
        self.draw_sphere(0.2, 32, 32)

        glPopMatrix()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

    def draw_sphere(self, radius, slices, stacks):
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, radius, slices, stacks)

    def update_animation(self):
        self.sun_angle += 0.5
        self.earth_angle += 2.0
        self.moon_angle += 5.0
        self.update()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.camera_angle_y += delta.x() / 5.0
            self.camera_angle_x += delta.y() / 5.0
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120.0
        self.camera_distance -= delta
        self.camera_distance = max(3.0, min(50.0, self.camera_distance))
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solar System - PyQt5")
        self.setGeometry(100, 100, 800, 600)
        self.gl_widget = SolarSystemWidget(self)
        self.setCentralWidget(self.gl_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Проверяем что OpenGL доступен
    format = QSurfaceFormat()
    format.setVersion(3, 2)
    format.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(format)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())