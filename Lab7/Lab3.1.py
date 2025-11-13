import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimer
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

# Совместимые шейдеры для OpenGL 2.1 / GLSL 1.20
VERTEX_SHADER = """
#version 120

attribute vec3 position;

uniform float progress;
uniform mat4 projection_view;

void main()
{
    vec3 initial_position = vec3(position.x, position.y, position.x * position.x + position.y * position.y);
    vec3 final_position = vec3(position.x, position.y, position.x * position.x - position.y * position.y);
    vec3 morphed_position = mix(initial_position, final_position, progress);

    gl_Position = projection_view * vec4(morphed_position, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 120

void main()
{
    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
}
"""

# Альтернативные ultra-совместимые шейдеры
VERTEX_SHADER_COMPAT = """
attribute vec3 position;

uniform float progress;
uniform mat4 projection_view;

void main()
{
    vec3 initial_position = vec3(position.x, position.y, position.x * position.x + position.y * position.y);
    vec3 final_position = vec3(position.x, position.y, position.x * position.x - position.y * position.y);
    vec3 morphed_position = initial_position + (final_position - initial_position) * progress;

    gl_Position = projection_view * vec4(morphed_position, 1.0);
}
"""

FRAGMENT_SHADER_COMPAT = """
void main()
{
    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
}
"""


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Morphing - PySide6")
        self.setGeometry(300, 300, 800, 600)
        self.progress = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(16)
        self.direction = 1
        self.speed = 0.05

        # Инициализация матриц (будет обновлено в resizeGL)
        self.view_matrix = np.identity(4, dtype=np.float32)
        self.projection_matrix = np.identity(4, dtype=np.float32)
        self.projection_view_matrix = np.identity(4, dtype=np.float32)

        self.program = None

    def initializeGL(self):
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode('utf-8')}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8')}")

        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)

        # Пробуем разные версии шейдеров
        shader_versions = [
            (VERTEX_SHADER, FRAGMENT_SHADER),
            (VERTEX_SHADER_COMPAT, FRAGMENT_SHADER_COMPAT)
        ]

        for vert_src, frag_src in shader_versions:
            try:
                self.program = compileProgram(
                    compileShader(vert_src, GL_VERTEX_SHADER),
                    compileShader(frag_src, GL_FRAGMENT_SHADER)
                )
                print("Shaders compiled successfully!")
                break
            except Exception as e:
                print(f"Shader compilation failed: {e}")
                continue

        # Если шейдеры не скомпилировались, используем фиксированный конвейер
        if self.program is None:
            print("Using fixed pipeline fallback")

        # Инициализируем матрицы
        self.update_matrices()

    def update_matrices(self):
        """Обновляет матрицы проекции и вида"""
        self.view_matrix = self.rotate_y(45) @ self.translate_z(-3.5) @ self.translate_x(-2.5)
        aspect = self.width() / self.height() if self.height() > 0 else 1.0
        self.projection_matrix = self.perspective(45, aspect, 0.1, 100)
        self.projection_view_matrix = np.dot(self.projection_matrix, self.view_matrix)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        self.update_matrices()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.program:
            # Используем шейдеры
            glUseProgram(self.program)

            # Устанавливаем uniform переменные
            progress_loc = glGetUniformLocation(self.program, "progress")
            if progress_loc != -1:
                glUniform1f(progress_loc, self.progress)

            projection_view_loc = glGetUniformLocation(self.program, "projection_view")
            if projection_view_loc != -1:
                glUniformMatrix4fv(projection_view_loc, 1, GL_TRUE, self.projection_view_matrix)

            self.draw_surface()
            glUseProgram(0)
        else:
            # Fallback: рисуем без шейдеров (простая белая поверхность)
            glColor3f(1.0, 1.0, 1.0)
            self.draw_surface_fixed()

    def draw_surface(self):
        """Рисует поверхность с помощью шейдеров"""
        rows, cols = 50, 50  # Уменьшил для производительности

        glBegin(GL_LINES)
        for i in range(rows - 1):
            for j in range(cols - 1):
                x0 = -1.0 + 2.0 * i / (rows - 1)
                y0 = -1.0 + 2.0 * j / (cols - 1)

                x1 = -1.0 + 2.0 * (i + 1) / (rows - 1)
                y1 = -1.0 + 2.0 * j / (cols - 1)

                x2 = -1.0 + 2.0 * i / (rows - 1)
                y2 = -1.0 + 2.0 * (j + 1) / (cols - 1)

                # Вычисляем z-координаты с морфингом
                z0_initial = x0 * x0 + y0 * y0
                z0_final = x0 * x0 - y0 * y0
                z0 = z0_initial + (z0_final - z0_initial) * self.progress

                z1_initial = x1 * x1 + y1 * y1
                z1_final = x1 * x1 - y1 * y1
                z1 = z1_initial + (z1_final - z1_initial) * self.progress

                z2_initial = x2 * x2 + y2 * y2
                z2_final = x2 * x2 - y2 * y2
                z2 = z2_initial + (z2_final - z2_initial) * self.progress

                glVertex3f(x0, y0, z0)
                glVertex3f(x1, y1, z1)

                glVertex3f(x1, y1, z1)
                glVertex3f(x2, y2, z2)

                glVertex3f(x2, y2, z2)
                glVertex3f(x0, y0, z0)
        glEnd()

    def draw_surface_fixed(self):
        """Рисует поверхность с помощью фиксированного конвейера"""
        rows, cols = 50, 50

        glBegin(GL_LINES)
        for i in range(rows - 1):
            for j in range(cols - 1):
                x0 = -1.0 + 2.0 * i / (rows - 1)
                y0 = -1.0 + 2.0 * j / (cols - 1)

                x1 = -1.0 + 2.0 * (i + 1) / (rows - 1)
                y1 = -1.0 + 2.0 * j / (cols - 1)

                x2 = -1.0 + 2.0 * i / (rows - 1)
                y2 = -1.0 + 2.0 * (j + 1) / (cols - 1)

                # Вычисляем z-координаты с морфингом
                z0_initial = x0 * x0 + y0 * y0
                z0_final = x0 * x0 - y0 * y0
                z0 = z0_initial + (z0_final - z0_initial) * self.progress

                z1_initial = x1 * x1 + y1 * y1
                z1_final = x1 * x1 - y1 * y1
                z1 = z1_initial + (z1_final - z1_initial) * self.progress

                z2_initial = x2 * x2 + y2 * y2
                z2_final = x2 * x2 - y2 * y2
                z2 = z2_initial + (z2_final - z2_initial) * self.progress

                glVertex3f(x0, y0, z0)
                glVertex3f(x1, y1, z1)

                glVertex3f(x1, y1, z1)
                glVertex3f(x2, y2, z2)

                glVertex3f(x2, y2, z2)
                glVertex3f(x0, y0, z0)
        glEnd()

    def update_progress(self):
        self.progress += self.direction * self.speed
        if self.progress >= 1.0:
            self.direction = -1
        elif self.progress <= 0.0:
            self.direction = 1
        self.update()

    def perspective(self, fov, aspect, near, far):
        f = 1.0 / math.tan(math.radians(fov) / 2)
        projection_matrix = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
            [0, 0, -1, 0]
        ], dtype=np.float32)
        return projection_matrix

    def rotate_y(self, angle):
        angle_rad = math.radians(angle)
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        rotation_matrix = np.array([
            [c, 0, -s, 0],
            [0, 1, 0, 0],
            [s, 0, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        return rotation_matrix

    def translate_z(self, z):
        translation_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        return translation_matrix

    def translate_x(self, x):
        translation_matrix = np.array([
            [1, 0, 0, x],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        return translation_matrix

    def closeEvent(self, event):
        self.timer.stop()
        if self.program:
            glDeleteProgram(self.program)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GLWidget()
    widget.show()
    sys.exit(app.exec())