import numpy as np


class Ray:
    def __init__(self, origin=None, direction=None):
        self.origin = origin if origin is not None else np.zeros(3, dtype=np.float32)
        self.direction = direction if direction is not None else np.zeros(3, dtype=np.float32)

        # Нормализуем направление
        if np.any(self.direction):
            self.direction = self.direction / np.linalg.norm(self.direction)

    def at(self, t):
        """Возвращает точку на луче на расстоянии t от origin"""
        return self.origin + self.direction * t

    # Свойства для совместимости с C# кодом
    @property
    def Origin(self):
        return self.origin

    @Origin.setter
    def Origin(self, value):
        self.origin = value

    @property
    def Direction(self):
        return self.direction

    @Direction.setter
    def Direction(self, value):
        self.direction = value
        if np.any(self.direction):
            self.direction = self.direction / np.linalg.norm(self.direction)