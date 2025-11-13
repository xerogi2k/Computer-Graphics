import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent, QVector3D, QMatrix4x4
from OpenGL.GL import *
import math
import time

from Shader import Shader
from Camera import Camera
from ChessLoader import ChessLoader
from ChessPiece import ChessPiece
from Model import Model


class ChessWindow(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Пути к моделям шахматных фигур
        self._paths = [
            "12936_Wooden_Chess_Knight_Side_B_V2_l31.obj",
            "WhiteKing.obj",
            "BlackKing.obj",
            "BlackKnight.obj",
            "WhitePawn.obj",
            "BlackQween.obj",
        ]

        # Ходы фигур: (индекс_фигуры, целевая_позиция)
        self._moves = [
            (1, QVector3D(0.0, 0.0, -9.0)),  # Пешка е2-е4
            (4, QVector3D(-4.5, 0.0, 9.0)),
            (2, QVector3D(0.0, 0.0, -13.5)),
            (3, QVector3D(4.5, 0.0, 4.5)),
            (2, QVector3D(4.5, 0.0, -18.0)),
        ]

        self._shader = None
        self._models = []
        self._chess_pieces = []
        self._camera = None

        self._current_move_index = 0
        self._move_delay = 3.0  # Задержка между ходами
        self._time_since_last_move = 0.0

        self._first_move = True
        self._last_mouse_pos = None
        self._time = 0.0

        # Таймер для обновления кадров
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(16)  # ~60 FPS

        # Отслеживание нажатых клавиш
        self._keys_pressed = set()

        # Настройка виджета
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

    def initializeGL(self):
        print("ChessWindow: OpenGL context ready")

        glEnable(GL_DEPTH_TEST)
        glClearColor(0.2, 0.3, 0.3, 1.0)

        try:
            # Загружаем шейдеры
            self._shader = Shader("Shaders/shader.vert", "Shaders/shader.frag")
            self._shader.use()

            # Загружаем модели шахматных фигур
            self._models = ChessLoader.load_chess(self._paths)

            # Создаем шахматные фигуры
            self._chess_pieces = [
                # Белые фигуры
                ChessPiece(self._models[1], QVector3D(0.0, 0.0, 0.0)),  # Белый король
                ChessPiece(self._models[4], QVector3D(0.0, 0.0, 0.0)),  # Белая пешка
                ChessPiece(self._models[5], QVector3D(0.0, 0.0, 0.0)),  # Белый ферзь

                # Черные фигуры
                ChessPiece(self._models[2], QVector3D(0.0, 0.0, 0.0)),  # Черный король
                ChessPiece(self._models[3], QVector3D(0.0, 0.0, 0.0)),  # Черный конь
            ]

            # Создаем камеру
            self._camera = Camera(QVector3D(0.0, 4.0, 3.0), self.width() / self.height())

            print("ChessWindow: Initialization complete")

        except Exception as e:
            print(f"ChessWindow: Initialization failed - {e}")
            import traceback
            traceback.print_exc()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        if self._camera:
            self._camera.aspect_ratio = w / h

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Проверяем что шейдер и камера инициализированы
        if not self._shader or not self._camera:
            return

        try:
            self._shader.use()

            # Устанавливаем освещение
            self._shader.set_vector3("lightPos", QVector3D(-15.0, -15.0, -15.0))
            self._shader.set_vector3("viewPos", self._camera.position)

            # Основная матрица модели (идентичная)
            model_matrix = QMatrix4x4()
            self._shader.set_matrix4("model", model_matrix)

            # Отрисовываем первую модель (доска?)
            if self._models:
                self._models[0].draw(self._shader)

            # Отрисовываем шахматные фигуры
            for piece in self._chess_pieces:
                # Создаем матрицу модели для каждой фигуры
                piece_model_matrix = QMatrix4x4()
                piece_model_matrix.translate(piece.position)

                self._shader.set_matrix4("model", piece_model_matrix)
                self._shader.set_matrix4("view", self._camera.get_view_matrix())
                self._shader.set_matrix4("projection", self._camera.get_projection_matrix())

                piece.model.draw(self._shader)

        except Exception as e:
            print(f"Render error: {e}")

    def _update(self):
        """Обновление состояния игры"""
        if not self.hasFocus() or not self._camera:
            return

        # Обработка ввода с клавиатуры
        self._process_keyboard_input()

        # Обновление анимации ходов
        self._time_since_last_move += 0.016  # ~60 FPS

        if (self._time_since_last_move >= self._move_delay and
                self._current_move_index < len(self._moves)):
            self._time_since_last_move = 0.0
            move = self._moves[self._current_move_index]
            piece_index, target_position = move
            self._chess_pieces[piece_index].move_to(target_position)
            self._current_move_index += 1

        # Обновляем позиции всех фигур
        for piece in self._chess_pieces:
            piece.update(0.016)  # deltaTime ~60 FPS

        self.update()

    def _process_keyboard_input(self):
        """Обработка ввода с клавиатуры"""
        # Проверяем что камера инициализирована
        if not self._camera:
            return

        camera_speed = 10.0
        sensitivity = 0.2

        if Qt.Key_W in self._keys_pressed:
            self._camera.position += self._camera.front * camera_speed * 0.016
        if Qt.Key_S in self._keys_pressed:
            self._camera.position -= self._camera.front * camera_speed * 0.016
        if Qt.Key_A in self._keys_pressed:
            self._camera.position -= self._camera.right * camera_speed * 0.016
        if Qt.Key_D in self._keys_pressed:
            self._camera.position += self._camera.right * camera_speed * 0.016
        if Qt.Key_Space in self._keys_pressed:
            self._camera.position += self._camera.up * camera_speed * 0.016
        if Qt.Key_Shift in self._keys_pressed:
            self._camera.position -= self._camera.up * camera_speed * 0.016

    def keyPressEvent(self, event: QKeyEvent):
        self._keys_pressed.add(event.key())

        if event.key() == Qt.Key_Escape:
            self.window().close()

    def keyReleaseEvent(self, event: QKeyEvent):
        self._keys_pressed.discard(event.key())

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Шахматы - OpenGL")
        self.setGeometry(100, 100, 1280, 720)

        self.chess_widget = ChessWindow()
        self.setCentralWidget(self.chess_widget)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()