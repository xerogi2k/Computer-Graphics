import math
from PySide6.QtGui import QVector3D, QMatrix4x4

class Camera:
    def __init__(self, position, aspect_ratio):
        self._front = -QVector3D(0.0, 0.0, 1.0)  # -Vector3.UnitZ
        self._up = QVector3D(0.0, 1.0, 0.0)      # Vector3.UnitY
        self._right = QVector3D(1.0, 0.0, 0.0)   # Vector3.UnitX

        self.position = position
        self.aspect_ratio = aspect_ratio
        self._fov = math.pi / 2  # MathHelper.PiOver2

        # Rotation around the X axis (radians)
        self._pitch = 0.0
        # Rotation around the Y axis (radians)
        self._yaw = -math.pi / 2  # -MathHelper.PiOver2

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
        return math.degrees(self._pitch)

    @pitch.setter
    def pitch(self, value):
        # Clamp between -89 and 89
        angle = max(-89.0, min(89.0, value))
        self._pitch = math.radians(angle)
        self.update_vectors()

    @property
    def yaw(self):
        return math.degrees(self._yaw)

    @yaw.setter
    def yaw(self, value):
        self._yaw = math.radians(value)
        self.update_vectors()

    @property
    def fov(self):
        return math.degrees(self._fov)

    @fov.setter
    def fov(self, value):
        # Clamp between 1 and 90
        angle = max(1.0, min(90.0, value))
        self._fov = math.radians(angle)

    def update_vectors(self):
        # Calculate front vector using trigonometry
        self._front.setX(math.cos(self._pitch) * math.cos(self._yaw))
        self._front.setY(math.sin(self._pitch))
        self._front.setZ(math.cos(self._pitch) * math.sin(self._yaw))

        # Normalize the vectors
        self._front = self._front.normalized()

        # Calculate right and up vectors using cross product
        self._right = QVector3D.crossProduct(self._front, QVector3D(0.0, 1.0, 0.0)).normalized()
        self._up = QVector3D.crossProduct(self._right, self._front).normalized()

    def get_view_matrix(self):
        view = QMatrix4x4()
        center = self.position + self._front
        view.lookAt(self.position, center, self._up)
        return view

    def get_projection_matrix(self):
        projection = QMatrix4x4()
        projection.perspective(math.degrees(self._fov), self.aspect_ratio, 0.01, 100.0)
        return projection