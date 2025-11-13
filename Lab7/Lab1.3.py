import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *

# Совместимые шейдеры для OpenGL 2.1 / GLSL 1.20
vertex_shader_source = """
#version 120

attribute vec4 position;
varying vec4 fragColor;

float CalculateRadius(float x)
{
    return (1.0 + sin(x)) *
           (1.0 + 0.9 * cos(8.0*x)) *
           (1.0 + 0.1 * cos(24.0 * x)) *
           (0.5 + 0.05 * cos(140.0 * x));
}

void main()
{
    float x = position.x;
    float R = CalculateRadius(x);

    vec4 newPosition;
    newPosition.x = R * cos(x) * 0.5;
    newPosition.y = R * sin(x) * 0.5;
    newPosition.z = position.z;
    newPosition.w = position.w;

    gl_Position = newPosition;

    // Передаем цвет через varying переменную
    float color_x = fract(x / (2.0 * 3.14159));
    fragColor = vec4(0.0, 1.0, 0.0, 1.0);  
}
"""

fragment_shader_source = """
#version 120

varying vec4 fragColor;

void main()
{
    gl_FragColor = fragColor;
}
"""

# Альтернативные ultra-совместимые шейдеры (без version директивы)
vertex_shader_compat = """
attribute vec4 position;
varying vec4 fragColor;

float CalculateRadius(float x)
{
    return (1.0 + sin(x)) *
           (1.0 + 0.9 * cos(8.0*x)) *
           (1.0 + 0.1 * cos(24.0 * x)) *
           (0.5 + 0.05 * cos(140.0 * x));
}

void main()
{
    float x = position.x;
    float R = CalculateRadius(x);

    vec4 newPosition;
    newPosition.x = R * cos(x) * 0.5;
    newPosition.y = R * sin(x) * 0.5;
    newPosition.z = position.z;
    newPosition.w = position.w;

    gl_Position = newPosition;

    // Передаем цвет через varying переменную
    float color_x = fract(x / (2.0 * 3.14159));
    fragColor = vec4(1.0 - color_x, 0.0, color_x, 1.0);
}
"""

fragment_shader_compat = """
varying vec4 fragColor;

void main()
{
    gl_FragColor = fragColor;
}
"""


class GLWidget(QOpenGLWidget):
    def initializeGL(self):
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode('utf-8')}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8')}")

        # Пробуем разные версии шейдеров
        shader_sources = [
            (vertex_shader_source, fragment_shader_source),  # Версия 120
            (vertex_shader_compat, fragment_shader_compat)  # Без версии
        ]

        for vert_src, frag_src in shader_sources:
            try:
                self.program = glCreateProgram()
                vertex_shader = glCreateShader(GL_VERTEX_SHADER)
                fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)

                glShaderSource(vertex_shader, vert_src)
                glShaderSource(fragment_shader, frag_src)

                glCompileShader(vertex_shader)
                if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
                    error = glGetShaderInfoLog(vertex_shader).decode()
                    print(f"Vertex shader compilation error: {error}")
                    glDeleteShader(vertex_shader)
                    glDeleteShader(fragment_shader)
                    glDeleteProgram(self.program)
                    continue

                glCompileShader(fragment_shader)
                if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
                    error = glGetShaderInfoLog(fragment_shader).decode()
                    print(f"Fragment shader compilation error: {error}")
                    glDeleteShader(vertex_shader)
                    glDeleteShader(fragment_shader)
                    glDeleteProgram(self.program)
                    continue

                glAttachShader(self.program, vertex_shader)
                glAttachShader(self.program, fragment_shader)

                glLinkProgram(self.program)

                if not glGetProgramiv(self.program, GL_LINK_STATUS):
                    error = glGetProgramInfoLog(self.program).decode()
                    print(f"Program linking error: {error}")
                    glDeleteShader(vertex_shader)
                    glDeleteShader(fragment_shader)
                    glDeleteProgram(self.program)
                    continue

                glDeleteShader(vertex_shader)
                glDeleteShader(fragment_shader)

                print("Shaders compiled successfully!")
                break

            except Exception as e:
                print(f"Shader error: {e}")
                continue
        else:
            print("All shader versions failed, using fixed pipeline")
            self.program = None

        # Создаем VBO для вершин
        self.vertices = []
        for i in range(1000):
            x = i * (2 * math.pi / 1000)
            self.vertices.extend([x, 0.0, 0.0, 1.0])  # x, y, z, w

        self.vertex_count = len(self.vertices) // 4

        # Создаем буферы
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER,
                     len(self.vertices) * 4,  # 4 bytes per float
                     (ctypes.c_float * len(self.vertices))(*self.vertices),
                     GL_STATIC_DRAW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.program:
            glUseProgram(self.program)

            # Устанавливаем атрибуты
            position_attr = glGetAttribLocation(self.program, "position")
            if position_attr != -1:
                glEnableVertexAttribArray(position_attr)
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
                glVertexAttribPointer(position_attr, 4, GL_FLOAT, GL_FALSE, 0, None)

            # Рисуем линию
            glDrawArrays(GL_LINE_STRIP, 0, self.vertex_count)

            if position_attr != -1:
                glDisableVertexAttribArray(position_attr)

            glUseProgram(0)
        else:
            # Fallback: рисуем простую линию без шейдеров
            glColor3f(1.0, 0.0, 1.0)  # Фиолетовый цвет
            glBegin(GL_LINE_STRIP)
            for i in range(1000):
                x = i * (2 * math.pi / 1000)
                R = (1.0 + math.sin(x)) * (1.0 + 0.9 * math.cos(8 * x)) * (1.0 + 0.1 * math.cos(24 * x)) * (
                            0.5 + 0.05 * math.cos(140 * x))
                glVertex2f(R * math.cos(x) * 0.5, R * math.sin(x) * 0.5)
            glEnd()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        aspect_ratio = w / h

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if aspect_ratio > 1:
            glOrtho(-2.5 * aspect_ratio, 2.5 * aspect_ratio, -2.5, 2.5, -1.0, 1.0)
        else:
            glOrtho(-2.5, 2.5, -2.5 / aspect_ratio, 2.5 / aspect_ratio, -1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def __del__(self):
        if hasattr(self, 'vbo'):
            glDeleteBuffers(1, [self.vbo])
        if hasattr(self, 'program') and self.program:
            glDeleteProgram(self.program)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.glWidget = GLWidget()
        layout.addWidget(self.glWidget)

        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.setGeometry(100, 100, 800, 600)
    mainWindow.setWindowTitle("Cannabola")
    mainWindow.show()
    sys.exit(app.exec())