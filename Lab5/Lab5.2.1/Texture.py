import os
from OpenGL.GL import *
from PIL import Image
import numpy as np


class Texture:
    def __init__(self, gl_handle):
        self.handle = gl_handle

    @staticmethod
    def load_from_file(path):
        """Загружает текстуру из файла"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Texture file not found: {path}")

        # Генерируем текстуру
        handle = glGenTextures(1)

        # Активируем и привязываем текстуру
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, handle)

        try:
            # Загружаем изображение с помощью PIL
            with Image.open(path) as img:
                # Конвертируем в RGBA если нужно
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                # Получаем данные изображения
                img_data = np.array(img)
                width, height = img.size

                # Загружаем данные в OpenGL
                glTexImage2D(
                    GL_TEXTURE_2D,  # target
                    0,  # level
                    GL_RGBA,  # internal format
                    width,  # width
                    height,  # height
                    0,  # border
                    GL_RGBA,  # format
                    GL_UNSIGNED_BYTE,  # type
                    img_data  # data
                )

        except Exception as e:
            glDeleteTextures([handle])
            raise Exception(f"Failed to load texture {path}: {e}")

        # Настройка параметров текстуры
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Генерация mipmaps
        glGenerateMipmap(GL_TEXTURE_2D)

        return Texture(handle)

    def use(self, unit=GL_TEXTURE0):
        """Активирует текстуру в указанном юните"""
        glActiveTexture(unit)
        glBindTexture(GL_TEXTURE_2D, self.handle)

    def __del__(self):
        """Деструктор для очистки ресурсов OpenGL"""
        try:
            if hasattr(self, 'handle'):
                glDeleteTextures([self.handle])
        except:
            pass  # Игнорируем ошибки если контекст OpenGL уже уничтожен