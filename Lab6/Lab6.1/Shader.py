import os
from OpenGL.GL import *
from PySide6.QtGui import QVector3D, QMatrix4x4
import ctypes
import numpy as np


class Shader:
    def __init__(self, vert_path, frag_path):
        # Проверяем существование файлов
        if not os.path.exists(vert_path):
            raise FileNotFoundError(f"Vertex shader not found: {vert_path}")
        if not os.path.exists(frag_path):
            raise FileNotFoundError(f"Fragment shader not found: {frag_path}")

        # Загружаем исходный код шейдеров
        with open(vert_path, 'r', encoding='utf-8') as f:
            vert_source = f.read()
        with open(frag_path, 'r', encoding='utf-8') as f:
            frag_source = f.read()

        print(f"Shader: Compiling {vert_path}, {frag_path}")

        # Компилируем вершинный шейдер
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vert_source)
        self.compile_shader(vertex_shader)  # Передаем только шейдер

        # Компилируем фрагментный шейдер
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, frag_source)
        self.compile_shader(fragment_shader)  # Передаем только шейдер

        # Создаем шейдерную программу
        self.handle = glCreateProgram()
        glAttachShader(self.handle, vertex_shader)
        glAttachShader(self.handle, fragment_shader)
        self.link_program()  # Без параметров - используем self.handle

        # Очищаем шейдеры
        glDetachShader(self.handle, vertex_shader)
        glDetachShader(self.handle, fragment_shader)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        # Кэшируем uniform locations
        self._uniform_locations = self.cache_uniform_locations()

        print("Shader: Program created successfully")

    def compile_shader(self, shader):
        """Компилирует шейдер и проверяет ошибки"""
        glCompileShader(shader)

        # Проверяем статус компиляции
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader)
            glDeleteShader(shader)
            raise Exception(f"Shader compilation error:\n{error}")

    def link_program(self):
        """Линкует шейдерную программу и проверяет ошибки"""
        glLinkProgram(self.handle)

        # Проверяем статус линковки
        if not glGetProgramiv(self.handle, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.handle)
            glDeleteProgram(self.handle)
            raise Exception(f"Program linking error:\n{error}")

    def cache_uniform_locations(self):
        """Кэширует locations всех uniform переменных"""
        uniform_locations = {}

        # Получаем количество активных uniform переменных
        uniform_count = glGetProgramiv(self.handle, GL_ACTIVE_UNIFORMS)

        for i in range(uniform_count):
            # Получаем информацию о uniform
            name_bytes, size, type = glGetActiveUniform(self.handle, i)
            name = name_bytes.decode('utf-8')

            # Убираем [0] из имен массивов (если есть)
            if name.endswith('[0]'):
                name = name[:-3]

            # Получаем location
            location = glGetUniformLocation(self.handle, name)
            uniform_locations[name] = location

            print(f"Shader: Uniform '{name}' -> location {location}")

        return uniform_locations

    def use(self):
        """Активирует шейдерную программу"""
        glUseProgram(self.handle)

    def get_attrib_location(self, attrib_name):
        """Получает location атрибута вершины"""
        return glGetAttribLocation(self.handle, attrib_name)

    def set_int(self, name, data):
        """Устанавливает uniform int"""
        self._set_uniform(name, lambda loc: glUniform1i(loc, data))

    def set_float(self, name, data):
        """Устанавливает uniform float"""
        self._set_uniform(name, lambda loc: glUniform1f(loc, data))

    def set_matrix4(self, name, matrix):
        """Устанавливает uniform matrix4"""

        def set_matrix(loc):
            # Конвертируем QMatrix4x4 в numpy array
            matrix_array = np.zeros(16, dtype=np.float32)
            for i in range(4):
                for j in range(4):
                    matrix_array[i * 4 + j] = matrix[i, j]
            glUniformMatrix4fv(loc, 1, GL_TRUE, matrix_array)

        self._set_uniform(name, set_matrix)

    def set_vector3(self, name, data):
        """Устанавливает uniform Vector3"""
        self._set_uniform(name, lambda loc: glUniform3f(loc, data.x(), data.y(), data.z()))

    def set_vector2(self, name, data):
        """Устанавливает uniform Vector2"""
        self._set_uniform(name, lambda loc: glUniform2f(loc, data.x(), data.y()))

    def _set_uniform(self, name, set_func):
        """Вспомогательный метод для установки uniform переменных"""
        if name in self._uniform_locations:
            location = self._uniform_locations[name]
            if location != -1:
                set_func(location)
            else:
                print(f"Shader: Uniform '{name}' location is -1")
        else:
            print(f"Shader: Uniform '{name}' not found in cached locations")

    def __del__(self):
        """Деструктор для очистки ресурсов OpenGL"""
        try:
            if hasattr(self, 'handle') and glDeleteProgram:
                glDeleteProgram(self.handle)
        except:
            pass