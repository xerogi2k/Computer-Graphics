import numpy as np
import random
from MathUtils import vector3


class AreaLight:
    def __init__(self, position=None, size=1.0, samples=16):
        self.position = position if position is not None else vector3(0, 5, 0)
        self.size = size
        self.samples = samples
        self.diffuse = np.ones(3, dtype=np.float32)
        self.specular = np.ones(3, dtype=np.float32)
        self.ambient = vector3(0.1, 0.1, 0.1)

    # Свойства для совместимости с C#
    @property
    def Position(self):
        return self.position

    @Position.setter
    def Position(self, value):
        self.position = value

    @property
    def Size(self):
        return self.size

    @Size.setter
    def Size(self, value):
        self.size = value

    @property
    def Samples(self):
        return self.samples

    @Samples.setter
    def Samples(self, value):
        self.samples = value

    @property
    def Diffuse(self):
        return self.diffuse

    @Diffuse.setter
    def Diffuse(self, value):
        self.diffuse = value

    @property
    def Specular(self):
        return self.specular

    @Specular.setter
    def Specular(self, value):
        self.specular = value

    @property
    def Ambient(self):
        return self.ambient

    @Ambient.setter
    def Ambient(self, value):
        self.ambient = value

    def get_samples_points(self):
        """Генерирует точки выборки на площади источника света"""
        points = []

        for i in range(self.samples):
            u = random.random()
            v = random.random()

            x = self.position[0] + (u - 0.5) * self.size
            y = self.position[1]
            z = self.position[2] + (v - 0.5) * self.size

            points.append(vector3(x, y, z))

        return points