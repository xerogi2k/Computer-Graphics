from Models.Ray import Ray
from Models.IntersectionResult import IntersectionResult
from Shapes.Interfaces.IShape import IShape


class Scene:
    def __init__(self):
        self.shapes = []
        self.lights = []

    # Свойства для совместимости с C#
    @property
    def Shapes(self):
        return self.shapes

    @Shapes.setter
    def Shapes(self, value):
        self.shapes = value

    @property
    def Lights(self):
        return self.lights

    @Lights.setter
    def Lights(self, value):
        self.lights = value

    def add(self, shape: IShape):
        """Добавляет объект в сцену"""
        self.shapes.append(shape)

    def add_light(self, light):
        """Добавляет источник света в сцену"""
        self.lights.append(light)

    def intersect(self, ray: Ray) -> IntersectionResult:
        """Находит ближайшее пересечение луча со сценой"""
        closest = IntersectionResult()  # По умолчанию нет пересечения

        for shape in self.shapes:
            intersection = shape.intersect(ray)
            # Используем is_valid() вместо прямого bool
            if intersection.is_valid() and intersection.distance < closest.distance:
                closest = intersection

        return closest