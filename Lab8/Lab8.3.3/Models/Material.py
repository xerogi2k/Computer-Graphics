import numpy as np


class Material:
    def __init__(self, diffuse=None, specular=None, ambient=None, shininess=32.0):
        self.diffuse = diffuse if diffuse is not None else np.ones(3, dtype=np.float32)
        self.specular = specular if specular is not None else np.ones(3, dtype=np.float32)
        self.ambient = ambient if ambient is not None else np.ones(3, dtype=np.float32)
        self.shininess = shininess

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

    @property
    def Shininess(self):
        return self.shininess

    @Shininess.setter
    def Shininess(self, value):
        self.shininess = value