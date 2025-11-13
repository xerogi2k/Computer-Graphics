from PySide6.QtGui import QVector3D
import math


class ChessPiece:
    def __init__(self, model, initial_position):
        self.model = model
        self.current_position = initial_position
        self.target_position = initial_position
        self.is_moving = False
        self.move_speed = 2.0  # Скорость перемещения

    @property
    def position(self):
        return self.current_position

    def move_to(self, new_position):
        self.target_position = new_position
        self.is_moving = True

    def update(self, delta_time):
        if self.is_moving:
            # Плавное перемещение к целевой позиции (Lerp)
            t = self.move_speed * delta_time
            t = min(t, 1.0)  # Ограничиваем до 1.0

            self.current_position = self.lerp(self.current_position, self.target_position, t)

            # Проверка достижения цели
            if self.distance(self.current_position, self.target_position) < 0.01:
                self.current_position = self.target_position
                self.is_moving = False

    @staticmethod
    def lerp(a, b, t):
        return QVector3D(
            a.x() + (b.x() - a.x()) * t,
            a.y() + (b.y() - a.y()) * t,
            a.z() + (b.z() - a.z()) * t
        )

    @staticmethod
    def distance(a, b):
        dx = b.x() - a.x()
        dy = b.y() - a.y()
        dz = b.z() - a.z()
        return math.sqrt(dx * dx + dy * dy + dz * dz)