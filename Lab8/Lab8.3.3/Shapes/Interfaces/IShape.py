from abc import ABC, abstractmethod
from Models.Ray import Ray
from Models.IntersectionResult import IntersectionResult

class IShape(ABC):
    @abstractmethod
    def intersect(self, ray: Ray) -> IntersectionResult:
        """Поиск пересечения луча с объектом"""
        pass