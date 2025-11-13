import math
from PySide6.QtGui import QVector3D, QMatrix4x4
from OpenGL.GL import *


class BuildingPart:
    def __init__(self, mesh, color, position, scale, rotation, texture=None, texture1=None):
        self._mesh = mesh
        self._color = color  # Добавил color, т.к. он есть в конструкторе
        self._position = position
        self._scale = scale
        self._rotation = rotation
        self._texture = texture
        self._texture1 = texture1

    def draw(self, shader):
        # Создаем модельную матрицу: масштаб -> поворот -> перемещение
        model = QMatrix4x4()
        model.scale(self._scale)
        model.rotate(self._rotation.x(), 1.0, 0.0, 0.0)  # Поворот вокруг X
        model.rotate(self._rotation.y(), 0.0, 1.0, 0.0)  # Поворот вокруг Y
        model.rotate(self._rotation.z(), 0.0, 0.0, 1.0)  # Поворот вокруг Z
        model.translate(self._position)

        # Устанавливаем uniform-переменные в шейдере
        shader.set_matrix4("model", model)
        shader.set_vector2("uvScale", QVector3D(2.0, 3.0, 0.0))  # QVector3D вместо Vector2

        # Активируем и привязываем текстуры
        if self._texture is not None:
            glActiveTexture(GL_TEXTURE0)
            self._texture.use()
            shader.set_int("texture0", 0)

        if self._texture1 is not None:
            glActiveTexture(GL_TEXTURE1)
            self._texture1.use()
            shader.set_int("texture1", 1)
            shader.set_int("useMultiTexturing", 1)
        else:
            shader.set_int("useMultiTexturing", 0)

        # Рисуем меш
        self._mesh.draw()