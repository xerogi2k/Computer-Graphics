from OpenGL.GL import *
import ctypes


class Mesh:
    def __init__(self, vertices, indices):
        self._index_count = len(indices)

        # Генерируем буферы
        self._vao = glGenVertexArrays(1)
        self._vbo = glGenBuffers(1)
        self._ebo = glGenBuffers(1)

        # Привязываем VAO
        glBindVertexArray(self._vao)

        # Загружаем данные вершин в VBO
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        vertices_data = (ctypes.c_float * len(vertices))(*vertices)
        glBufferData(GL_ARRAY_BUFFER,
                     len(vertices) * ctypes.sizeof(ctypes.c_float),
                     vertices_data, GL_STATIC_DRAW)

        # Загружаем индексы в EBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        indices_data = (ctypes.c_uint * len(indices))(*indices)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     len(indices) * ctypes.sizeof(ctypes.c_uint),
                     indices_data, GL_STATIC_DRAW)

        # Устанавливаем атрибуты вершин
        # layout(location = 0) in vec3 aPos;
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                              11 * ctypes.sizeof(ctypes.c_float),
                              ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # layout(location = 1) in vec3 aNormal;
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                              11 * ctypes.sizeof(ctypes.c_float),
                              ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(1)

        # layout(location = 2) in vec3 aColor;
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                              11 * ctypes.sizeof(ctypes.c_float),
                              ctypes.c_void_p(6 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(2)

        # layout(location = 3) in vec2 aTexCoord;
        glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE,
                              11 * ctypes.sizeof(ctypes.c_float),
                              ctypes.c_void_p(9 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(3)

        # Настройки текстур (перенесены из Mesh класса)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Отвязываем VAO
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self._vao)
        glDrawElements(GL_TRIANGLES, self._index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def __del__(self):
        """Деструктор для очистки ресурсов OpenGL"""
        try:
            if hasattr(self, '_vao'):
                glDeleteVertexArrays(1, [self._vao])
            if hasattr(self, '_vbo'):
                glDeleteBuffers(1, [self._vbo])
            if hasattr(self, '_ebo'):
                glDeleteBuffers(1, [self._ebo])
        except:
            pass  # Игнорируем ошибки если контекст OpenGL уже уничтожен