import numpy as np
import math
from Models.Ray import Ray
from Models.IntersectionResult import IntersectionResult
from Models.Material import Material
from Shapes.Interfaces.IShape import IShape
from MathUtils import dot, normalize


class InfinityChessBoard(IShape):
    def __init__(self, point=None, normal=None, material=None,
                 checker_size=2.0, color1=None, color2=None):
        self.point = point if point is not None else np.zeros(3, dtype=np.float32)
        self.normal = normalize(normal) if normal is not None else np.array([0, 1, 0], dtype=np.float32)
        self.checker_size = checker_size
        self.material = material if material is not None else Material()
        self.color1 = color1 if color1 is not None else np.zeros(3, dtype=np.float32)
        self.color2 = color2 if color2 is not None else np.ones(3, dtype=np.float32)

    # Свойства для совместимости с C#
    @property
    def Point(self):
        return self.point

    @Point.setter
    def Point(self, value):
        self.point = value

    @property
    def Normal(self):
        return self.normal

    @Normal.setter
    def Normal(self, value):
        self.normal = normalize(value)

    @property
    def Color1(self):
        return self.color1

    @Color1.setter
    def Color1(self, value):
        self.color1 = value

    @property
    def Color2(self):
        return self.color2

    @Color2.setter
    def Color2(self, value):
        self.color2 = value

    @property
    def CheckerSize(self):
        return self.checker_size

    @CheckerSize.setter
    def CheckerSize(self, value):
        self.checker_size = value

    @property
    def Material(self):
        return self.material

    @Material.setter
    def Material(self, value):
        self.material = value

    def intersect(self, ray: Ray) -> IntersectionResult:
        result = IntersectionResult()

        denom = dot(self.normal, ray.direction)

        if abs(denom) < 1e-6:
            return result  # Нет пересечения

        t = dot(self.point - ray.origin, self.normal) / denom

        if t < 0:
            return result  # Пересечение позади луча

        point = ray.at(t)

        result.point = point
        result.distance = t
        result.color = self._get_color(point)
        result.material = self.material
        result.normal = self.normal
        result.shape = self

        return result

    def _get_color(self, point):
        u = point[0] / self.checker_size
        v = point[2] / self.checker_size  # Используем Z вместо Y для шахматной доски

        iu = int(math.floor(u))
        iv = int(math.floor(v))

        if (iu + iv) % 2 == 0:
            return self.color1
        else:
            return self.color2