import os
import numpy as np
from OpenGL.GL import *
import ctypes
from Texture import Texture


class Model:
    def __init__(self, path):
        self._vao = 0
        self._vbo = 0
        self._ebo = 0
        self._vertex_count = 0
        self._textures = []

        self.load_model(path)

    def load_model(self, path):
        #Загружает 3D модель из файла
        print(f"Loading model: {path}")

        # ВРЕМЕННО: создаем простой куб вместо использования Assimp
        # Позже можно добавить поддержку pyassimp или других библиотек
        if not os.path.exists(path):
            print(f"Model file not found: {path}, creating test cube")
            self.create_test_cube()
            return

        try:
            # TODO: Добавить поддержку загрузки реальных моделей через pyassimp
            # Пока создаем тестовый куб
            self.create_test_cube()

        except Exception as e:
            print(f"Failed to load model {path}: {e}")
            print("Creating test cube instead")
            self.create_test_cube()

    def create_test_cube(self):
        #Создает тестовый куб для демонстрации
        # Вершины куба: позиция(x,y,z), нормаль(nx,ny,nz), цвет(r,g,b), текстурные координаты(u,v)
        vertices = [
            # Передняя грань
            -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0,
            0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0,
            0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0,

            # Задняя грань
            -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.0,
            0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 1.0,
            -0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0, 1.0,

            # Левая грань
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            -0.5, -0.5, 0.5, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0,
            -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0,
            -0.5, 0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,

            # Правая грань
            0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0,
            0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0,
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0,
            0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0,

            # Верхняя грань
            -0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0,
            0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0,
            0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0,
            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0,

            # Нижняя грань
            -0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0,
            0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0,
            0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0,
        ]

        indices = [
            # Передняя грань
            0, 1, 2, 2, 3, 0,
            # Задняя грань
            6, 5, 4, 4, 7, 6,
            # Левая грань
            8, 9, 10, 10, 11, 8,
            # Правая грань
            14, 13, 12, 12, 15, 14,
            # Верхняя грань
            18, 17, 16, 16, 19, 18,
            # Нижняя грань
            20, 21, 22, 22, 23, 20
        ]

        self._vertex_count = len(indices)

        # Создаем VAO, VBO и EBO
        self._vao = glGenVertexArrays(1)
        self._vbo = glGenBuffers(1)
        self._ebo = glGenBuffers(1)

        glBindVertexArray(self._vao)

        # VBO
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        vertices_data = (ctypes.c_float * len(vertices))(*vertices)
        glBufferData(GL_ARRAY_BUFFER, len(vertices) * ctypes.sizeof(ctypes.c_float),
                     vertices_data, GL_STATIC_DRAW)

        # EBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        indices_data = (ctypes.c_uint * len(indices))(*indices)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * ctypes.sizeof(ctypes.c_uint),
                     indices_data, GL_STATIC_DRAW)

        # Настройка атрибутов вершин (11 floats per vertex)
        stride = 11 * ctypes.sizeof(ctypes.c_float)

        # Атрибут 0: Позиция
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Атрибут 1: Нормали
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride,
                              ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(1)

        # Атрибут 2: Цвет
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride,
                              ctypes.c_void_p(6 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(2)

        # Атрибут 3: Текстурные координаты
        glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, stride,
                              ctypes.c_void_p(9 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(3)

        glBindVertexArray(0)

        print(f"Test cube created with {len(vertices) // 11} vertices, {self._vertex_count} indices")

    def draw(self, shader):
        # Отрисовывает модель
        # Активируем текстуру (если есть)
        if self._textures:
            glActiveTexture(GL_TEXTURE0)
            self._textures[0].use()
            shader.set_int("texture0", 0)

        # Рендерим модель
        glBindVertexArray(self._vao)
        glDrawElements(GL_TRIANGLES, self._vertex_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def __del__(self):
        #Деструктор для очистки ресурсов OpenGL
        try:
            if hasattr(self, '_vao'):
                glDeleteVertexArrays(1, [self._vao])
            if hasattr(self, '_vbo'):
                glDeleteBuffers(1, [self._vbo])
            if hasattr(self, '_ebo'):
                glDeleteBuffers(1, [self._ebo])
        except:
            pass