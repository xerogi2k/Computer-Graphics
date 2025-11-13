import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram


class OpenGLWidget(QOpenGLWidget):
    def initializeGL(self):
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode('utf-8')}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8')}")

        # Совместимые шейдеры для OpenGL 2.1 / GLSL 1.20
        vertex_shader = """
        #version 120
        attribute vec3 position;
        void main()
        {
            gl_Position = vec4(position, 1.0);
        }
        """

        fragment_shader = """
        #version 120
        uniform vec2 center;

        void main()
        {
            float radius = 0.5;
            float thickness = 0.025;
            vec2 center = vec2(0.0, 0.0);
            vec2 fragCoord = vec2(gl_FragCoord.x / 450.0, gl_FragCoord.y / 450.0);
            float dist = distance(center, fragCoord);

            if (dist > radius - thickness && dist < radius + thickness) 
            {
                gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);  // Черное кольцо
            } 
            else if (dist < radius) 
            {
                gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);  // Белая внутренняя часть
            } 
            else 
            {
                discard;
            }
        }
        """

        # Альтернативные ultra-совместимые шейдеры
        vertex_shader_compat = """
        attribute vec3 position;
        void main()
        {
            gl_Position = gl_ModelViewProjectionMatrix * vec4(position, 1.0);
        }
        """

        fragment_shader_compat = """
        void main()
        {
            float radius = 0.5;
            float thickness = 0.025;
            vec2 center = vec2(0.5, 0.5);
            vec2 fragCoord = gl_TexCoord[0].st;
            float dist = distance(center, fragCoord);

            if (dist > radius - thickness && dist < radius + thickness) 
            {
                gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
            } 
            else if (dist < radius) 
            {
                gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
            } 
            else 
            {
                discard;
            }
        }
        """

        # Пробуем разные версии шейдеров
        shader_versions = [
            (vertex_shader, fragment_shader),
            (vertex_shader_compat, fragment_shader_compat)
        ]

        self.program = None
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

        # Если шейдеры не скомпилировались, будем использовать фиксированный конвейер
        if self.program is None:
            print("Using fixed pipeline fallback")

        # Белый фон
        glClearColor(1.0, 1.0, 1.0, 1.0)

        # Вершины полноэкранного квада
        self.vertices = [
            -1.0, -1.0, 0.0,
            1.0, -1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, 1.0, 0.0
        ]

        # Создаем VBO (совместимый способ)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER,
                     len(self.vertices) * 4,  # 4 bytes per float
                     (GLfloat * len(self.vertices))(*self.vertices),
                     GL_STATIC_DRAW)

        # Пробуем создать VAO, но если не поддерживается - работаем без него
        try:
            self.vao = glGenVertexArrays(1)
            glBindVertexArray(self.vao)
            print("VAO supported")
        except:
            self.vao = None
            print("VAO not supported, using legacy mode")

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        if self.program:
            # Используем шейдеры
            glUseProgram(self.program)

            # Устанавливаем uniform переменные
            center_location = glGetUniformLocation(self.program, "center")
            if center_location != -1:
                glUniform2f(center_location, 0.0, 0.0)

            # Устанавливаем атрибуты вершин
            position_attr = glGetAttribLocation(self.program, "position")
            if position_attr != -1:
                glEnableVertexAttribArray(position_attr)
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
                glVertexAttribPointer(position_attr, 3, GL_FLOAT, GL_FALSE, 0, None)

            # Рисуем квад
            glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

            # Отключаем атрибуты
            if position_attr != -1:
                glDisableVertexAttribArray(position_attr)

            glUseProgram(0)
        else:
            # Fallback: рисуем кольцо с помощью фиксированного конвейера
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(-1, 1, -1, 1, -1, 1)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Рисуем белый диск
            glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(0.0, 0.0)
            for i in range(37):  # 36 сегментов + замыкание
                angle = i * 2.0 * math.pi / 36
                glVertex2f(0.5 * math.cos(angle), 0.5 * math.sin(angle))
            glEnd()

            # Рисуем черное кольцо поверх
            glColor3f(0.0, 0.0, 0.0)
            glBegin(GL_TRIANGLE_STRIP)
            for i in range(37):
                angle = i * 2.0 * math.pi / 36
                # Внешний радиус кольца
                glVertex2f((0.5 + 0.025) * math.cos(angle), (0.5 + 0.025) * math.sin(angle))
                # Внутренний радиус кольца
                glVertex2f((0.5 - 0.025) * math.cos(angle), (0.5 - 0.025) * math.sin(angle))
            glEnd()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def __del__(self):
        # Очистка ресурсов
        if hasattr(self, 'vbo'):
            glDeleteBuffers(1, [self.vbo])
        if hasattr(self, 'vao') and self.vao:
            glDeleteVertexArrays(1, [self.vao])
        if hasattr(self, 'program') and self.program:
            glDeleteProgram(self.program)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ring Visualization - PySide6")
        self.setGeometry(100, 100, 900, 900)

        self.glWidget = OpenGLWidget()
        self.setCentralWidget(self.glWidget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())