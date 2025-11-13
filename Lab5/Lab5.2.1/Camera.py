import math
from PySide6.QtGui import QVector3D, QMatrix4x4


class Camera:
    def __init__(self, position, aspect_ratio):
        self._front = -QVector3D(0.0, 0.0, 1.0)  # -Vector3.UnitZ
        self._up = QVector3D(0.0, 1.0, 0.0)  # Vector3.UnitY
        self._right = QVector3D(1.0, 0.0, 0.0)  # Vector3.UnitX

        self.position = position
        self.aspect_ratio = aspect_ratio
        self.fov = 45.0

        self._pitch = 0.0
        self._yaw = -90.0

        self.update_vectors()

    @property
    def front(self):
        return self._front

    @property
    def up(self):
        return self._up

    @property
    def right(self):
        return self._right

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, value):
        self._pitch = max(-89.0, min(89.0, value))  # Math.Clamp equivalent
        self.update_vectors()

    @property
    def yaw(self):
        return self._yaw

    @yaw.setter
    def yaw(self, value):
        self._yaw = value
        self.update_vectors()

    def update_vectors(self):
        # Конвертируем углы в радианы
        pitch_rad = math.radians(self._pitch)
        yaw_rad = math.radians(self._yaw)

        # Вычисляем новый вектор front
        self._front.setX(math.cos(pitch_rad) * math.cos(yaw_rad))
        self._front.setY(math.sin(pitch_rad))
        self._front.setZ(math.cos(pitch_rad) * math.sin(yaw_rad))

        # Нормализуем
        self._front = self._front.normalized()

        # Вычисляем right и up векторы
        self._right = QVector3D.crossProduct(self._front, QVector3D(0.0, 1.0, 0.0)).normalized()
        self._up = QVector3D.crossProduct(self._right, self._front).normalized()

    def get_view_matrix(self):
        view = QMatrix4x4()
        # QMatrix4x4.lookAt принимает: eye, center, up
        center = self.position + self._front
        view.lookAt(self.position, center, self._up)
        return view

    def get_projection_matrix(self):
        projection = QMatrix4x4()
        fov_rad = math.radians(self.fov)
        projection.perspective(fov_rad, self.aspect_ratio, 0.1, 100.0)
        return projection