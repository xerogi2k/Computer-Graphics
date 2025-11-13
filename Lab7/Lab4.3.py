import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt
from OpenGL.GL import *
import numpy as np


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mandelbrot - PySide6")
        self.setGeometry(300, 300, 800, 600)
        self.area_w = np.array([-2.0, 1.0], dtype=np.float32)
        self.area_h = np.array([-1.0, 1.0], dtype=np.float32)
        self.max_iterations = 100
        self.zoom_factor = 0.1
        self.last_pos = None

        # Создаем простую палитру вручную
        self.fractal = self.create_fractal(256)

    def create_fractal(self, size):
        """Создает цветовую палитру"""
        fractal = []
        for i in range(size):
            t = i / size
            # Красивый градиент от синего к красному
            r = int(255 * (0.5 + 0.5 * math.sin(2 * math.pi * t + 0)))
            g = int(255 * (0.5 + 0.5 * math.sin(2 * math.pi * t + 2)))
            b = int(255 * (0.5 + 0.5 * math.sin(2 * math.pi * t + 4)))
            fractal.append((r, g, b))
        return fractal

    def mandelbrot_iteration(self, cx, cy):
        """Вычисляет количество итераций для точки (cx, cy)"""
        x, y = 0.0, 0.0
        for i in range(self.max_iterations):
            x2 = x * x
            y2 = y * y
            if x2 + y2 > 4.0:
                return i
            y = 2 * x * y + cy
            x = x2 - y2 + cx
        return self.max_iterations

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        zoom_factor = 1 + delta * self.zoom_factor

        # Масштабирование с сохранением центра
        center_x = (self.area_w[1] + self.area_w[0]) / 2
        center_y = (self.area_h[1] + self.area_h[0]) / 2

        width = (self.area_w[1] - self.area_w[0]) * zoom_factor
        height = (self.area_h[1] - self.area_h[0]) * zoom_factor

        self.area_w = np.array([center_x - width / 2, center_x + width / 2])
        self.area_h = np.array([center_y - height / 2, center_y + height / 2])

        self.update()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.last_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.last_pos:
            current_pos = event.position().toPoint()
            dx = current_pos.x() - self.last_pos.x()
            dy = self.last_pos.y() - current_pos.y()  # Инвертируем Y

            area_width = self.area_w[1] - self.area_w[0]
            area_height = self.area_h[1] - self.area_h[0]

            dx_scaled = dx * area_width / self.width()
            dy_scaled = dy * area_height / self.height()

            self.area_w -= dx_scaled
            self.area_h -= dy_scaled

            self.last_pos = current_pos
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = None

    def initializeGL(self):
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode('utf-8')}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8')}")

        # Простая настройка OpenGL
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_TEXTURE_2D)

        # Создаем текстуру для палитры
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # Преобразуем палитру в формат для текстуры
        texture_data = []
        for color in self.fractal:
            texture_data.extend(color)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, len(self.fractal), 1, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, bytes(texture_data))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Устанавливаем ортографическую проекцию
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width(), 0, self.height(), -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Рисуем фрактал точками
        glBegin(GL_POINTS)

        for x in range(self.width()):
            for y in range(self.height()):
                # Преобразуем координаты экрана в координаты фрактала
                cx = self.area_w[0] + (self.area_w[1] - self.area_w[0]) * x / self.width()
                cy = self.area_h[0] + (self.area_h[1] - self.area_h[0]) * y / self.height()

                # Вычисляем итерации
                iterations = self.mandelbrot_iteration(cx, cy)

                if iterations == self.max_iterations:
                    # Точка внутри множества - черный цвет
                    glColor3f(0.0, 0.0, 0.0)
                else:
                    # Точка вне множества - цвет из палитры
                    color_index = int((iterations / self.max_iterations) * (len(self.fractal) - 1))
                    r, g, b = self.fractal[color_index]
                    glColor3f(r / 255.0, g / 255.0, b / 255.0)

                glVertex2f(x, y)

        glEnd()

    def keyPressEvent(self, event):
        step = 10

        if event.key() == Qt.Key_Down:
            dx = 0
            dy = step
        elif event.key() == Qt.Key_Up:
            dx = 0
            dy = -step
        elif event.key() == Qt.Key_Right:
            dx = -step
            dy = 0
        elif event.key() == Qt.Key_Left:
            dx = step
            dy = 0
        elif event.key() == Qt.Key_Plus:
            self.max_iterations = min(1000, self.max_iterations + 50)
            print(f"Max iterations: {self.max_iterations}")
            self.update()
            return
        elif event.key() == Qt.Key_Minus:
            self.max_iterations = max(50, self.max_iterations - 50)
            print(f"Max iterations: {self.max_iterations}")
            self.update()
            return
        elif event.key() == Qt.Key_R:
            # Сброс к начальному виду
            self.area_w = np.array([-2.0, 1.0], dtype=np.float32)
            self.area_h = np.array([-1.0, 1.0], dtype=np.float32)
            self.max_iterations = 100
            self.update()
            return
        else:
            return

        area_width = self.area_w[1] - self.area_w[0]
        area_height = self.area_h[1] - self.area_h[0]
        dx_scaled = dx * area_width / self.width()
        dy_scaled = dy * area_height / self.height()
        self.area_w -= dx_scaled
        self.area_h -= dy_scaled

        self.update()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mandelbrot Set Viewer")
        self.glWidget = GLWidget()
        self.setCentralWidget(self.glWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()

    print("Управление:")
    print("- Колесо мыши: масштабирование")
    print("- ЛКМ + перемещение: панорамирование")
    print("- +/-: увеличить/уменьшить детализацию")
    print("- Стрелки: перемещение")
    print("- R: сброс к начальному виду")

    sys.exit(app.exec())