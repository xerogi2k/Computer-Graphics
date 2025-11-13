import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Models.Material import Material
    from Shapes.Interfaces.IShape import IShape


class IntersectionResult:
    def __init__(self):
        self.point = np.zeros(3, dtype=np.float32)
        self.distance = float('inf')
        self.normal = np.zeros(3, dtype=np.float32)
        self.color = np.ones(3, dtype=np.float32)
        self.material = None  # type: Material
        self.shape = None  # type: IShape

    def is_valid(self):
        """Проверяет, было ли пересечение"""
        return self.distance < float('inf')

    # Для обратной совместимости можно оставить __bool__, но возвращать обычный bool
    def __bool__(self):
        return bool(self.is_valid())