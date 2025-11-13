import os
from OpenGL.GL import *
from PySide6.QtGui import QVector3D, QMatrix4x4
import ctypes


class Shader:
    def __init__(self, vert_path, frag_path):
        # Загружаем исходный код шейдеров из файлов
        vert_source = self._load_shader_source(vert_path)
        frag_source = self._load_shader_source(frag_path)

        # Компилируем вершинный шейдер
        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vert_shader, vert_source)
        glCompileShader(vert_shader)

        # Проверяем компиляцию вершинного шейдера
        if not glGetShaderiv(vert_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vert_shader)
            raise Exception(f"Vertex shader compilation error: {error}")

        # Компилируем фрагментный шейдер
        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(frag_shader, frag_source)
        glCompileShader(frag_shader)

        # Проверяем компиляцию фрагментного шейдера
        if not glGetShaderiv(frag_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(frag_shader)
            raise Exception(f"Fragment shader compilation error: {error}")

        # Создаем шейдерную программу
        self.handle = glCreateProgram()
        glAttachShader(self.handle, vert_shader)
        glAttachShader(self.handle, frag_shader)
        glLinkProgram(self.handle)

        # Проверяем линковку
        if not glGetProgramiv(self.handle, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.handle)
            raise Exception(f"Shader program linking error: {error}")

        # Очищаем шейдеры
        glDetachShader(self.handle, vert_shader)
        glDetachShader(self.handle, frag_shader)
        glDeleteShader(vert_shader)
        glDeleteShader(frag_shader)

        # Кэш uniform локаций
        self._uniform_locations = {}
        self._cache_uniform_locations()

    def _load_shader_source(self, file_path):
        """Загружает исходный код шейдера из файла"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Shader file not found: {file_path}")

        with open(file_path, 'r') as f:
            return f.read()

    def _cache_uniform_locations(self):
        """Кэширует все uniform переменные в шейдере"""
        uniform_count = glGetProgramiv(self.handle, GL_ACTIVE_UNIFORMS)

        for i in range(uniform_count):
            name, size, type = glGetActiveUniform(self.handle, i)
            location = glGetUniformLocation(self.handle, name)
            self._uniform_locations[name] = location

    def _get_uniform_location(self, name):
        """Получает location uniform переменной (с кэшированием)"""
        if name in self._uniform_locations:
            return self._uniform_locations[name]

        location = glGetUniformLocation(self.handle, name)
        self._uniform_locations[name] = location
        return location

    def use(self):
        """Активирует шейдерную программу"""
        glUseProgram(self.handle)

    def set_matrix4(self, name, matrix):
        """Устанавливает uniform матрицу 4x4"""
        location = self._get_uniform_location(name)
        if location != -1:
            # Конвертируем QMatrix4x4 в массив float для OpenGL
            matrix_data = []
            for i in range(4):
                for j in range(4):
                    matrix_data.append(matrix(i, j))

            glUniformMatrix4fv(location, 1, GL_FALSE, (ctypes.c_float * 16)(*matrix_data))

    def set_int(self, name, value):
        """Устанавливает uniform integer"""
        location = self._get_uniform_location(name)
        if location != -1:
            glUniform1i(location, value)

    def set_vector3(self, name, value):
        """Устанавливает uniform vector3"""
        location = self._get_uniform_location(name)
        if location != -1:
            glUniform3f(location, value.x(), value.y(), value.z())

    def set_vector2(self, name, value):
        """Устанавливает uniform vector2"""
        location = self._get_uniform_location(name)
        if location != -1:
            glUniform2f(location, value.x(), value.y())

    def __del__(self):
        """Деструктор для очистки ресурсов OpenGL"""
        try:
            if hasattr(self, 'handle'):
                glDeleteProgram(self.handle)
        except:
            pass  # Игнорируем ошибки если контекст OpenGL уже уничтожен