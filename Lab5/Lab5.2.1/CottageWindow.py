import math
from PySide6.QtOpenGLWidgets import QOpenGLWidget  # ИЗМЕНЕНО!
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtGui import QVector3D, QMatrix4x4  # ДОБАВЛЕНО!
from OpenGL.GL import *

from Shader import Shader
from CottageScene import CottageScene
from Camera import Camera


class CottageWindow(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._shader = None
        self._scene = None
        self._camera = None
        self._first_move = True
        self._last_mouse_pos = None
        self._fog_enabled = True

        # Таймер для обновления кадров
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(16)  # ~60 FPS

        # Отслеживание нажатых клавиш
        self._keys_pressed = set()

        # Настройка виджета
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

    def initializeGL(self):
        glClearColor(0.53, 0.81, 0.92, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        # Загрузка шейдеров и создание сцены
        self._shader = Shader("Shaders/shader.vert", "Shaders/shader.frag")
        self._camera = Camera(
            position=QVector3D(0, 5, 15),
            aspect_ratio=self.width() / self.height()
        )
        self._scene = CottageScene()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        self._camera.aspect_ratio = w / h

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self._shader and self._scene:
            self._shader.use()
            self._shader.set_matrix4("view", self._camera.get_view_matrix())
            self._shader.set_matrix4("projection", self._camera.get_projection_matrix())
            self._shader.set_int("fogEnabled", 1 if self._fog_enabled else 0)

            self._scene.draw(self._shader)

    def keyPressEvent(self, event: QKeyEvent):
        self._keys_pressed.add(event.key())

        # Выход по Escape
        if event.key() == Qt.Key_Escape:
            self.window().close()

        # Переключение тумана по F
        if event.key() == Qt.Key_F:
            self._fog_enabled = not self._fog_enabled

    def keyReleaseEvent(self, event: QKeyEvent):
        self._keys_pressed.discard(event.key())

    def process_input(self):
        if not self.hasFocus():
            return

        camera_speed = 0.1  # Фиксированная скорость вместо time-based
        sensitivity = 0.2

        # Обработка движения камеры
        if Qt.Key_W in self._keys_pressed:
            self._camera.position += self._camera.front * camera_speed
        if Qt.Key_S in self._keys_pressed:
            self._camera.position -= self._camera.front * camera_speed
        if Qt.Key_A in self._keys_pressed:
            self._camera.position -= self._camera.right * camera_speed
        if Qt.Key_D in self._keys_pressed:
            self._camera.position += self._camera.right * camera_speed
        if Qt.Key_Space in self._keys_pressed:
            self._camera.position += self._camera.up * camera_speed
        if Qt.Key_Shift in self._keys_pressed:
            self._camera.position -= self._camera.up * camera_speed

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._first_move = True
            self.setCursor(Qt.BlankCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)
            self._first_move = True

    def mouseMoveEvent(self, event: QMouseEvent):
        # Проверяем что камера инициализирована
        if not self._camera or not self.hasFocus() or not (event.buttons() & Qt.LeftButton):
            return

        current_pos = event.position()

        if self._first_move:
            self._last_mouse_pos = current_pos
            self._first_move = False
            return

        delta_x = current_pos.x() - self._last_mouse_pos.x()
        delta_y = current_pos.y() - self._last_mouse_pos.y()
        self._last_mouse_pos = current_pos

        self._camera.yaw += delta_x * 0.1  # sensitivity
        self._camera.pitch -= delta_y * 0.1

    def wheelEvent(self, event: QWheelEvent):
        # Проверяем что камера инициализирована
        if not self._camera:
            return

        delta = event.angleDelta().y() / 120.0
        self._camera.fov -= delta
        self._camera.fov = max(1.0, min(90.0, self._camera.fov))

    def update(self):
        self.process_input()
        super().update()
