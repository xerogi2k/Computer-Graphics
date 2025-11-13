import os
from PySide6.QtGui import QVector3D
from BuildingPart import BuildingPart
from Mesh import Mesh
from Texture import Texture


class CottageScene:
    def __init__(self):
        self._parts = []

        # Цвета материалов
        self._brick_color = QVector3D(0.6, 0.2, 0.1)
        self._window_color = QVector3D(0.8, 0.9, 1.0)
        self._wood_color = QVector3D(0.5, 0.35, 0.2)
        self._ground_color = QVector3D(0.2, 0.6, 0.3)

        # Загрузка текстур
        resources_path = "Resources"
        self._brick_texture = Texture.load_from_file(os.path.join(resources_path, "brick.png"))
        self._terrain_texture = Texture.load_from_file(os.path.join(resources_path, "terrain1.png"))
        self._door_texture = Texture.load_from_file(os.path.join(resources_path, "door.png"))
        self._garage_texture = Texture.load_from_file(os.path.join(resources_path, "garage.png"))
        self._window_texture = Texture.load_from_file(os.path.join(resources_path, "window1.png"))
        self._terrain_second_texture = Texture.load_from_file(os.path.join(resources_path, "terrain.png"))

        # Создаем меши один раз
        cube_mesh = self.create_cube_mesh()
        roof_mesh = self.create_roof_mesh()
        plane_mesh = self.create_plane_mesh()

        # Строим сцену
        self.build_scene(cube_mesh, roof_mesh, plane_mesh)

    def build_scene(self, cube_mesh, roof_mesh, plane_mesh):
        # Гараж
        self._parts.append(BuildingPart(
            cube_mesh, self._brick_color,
            QVector3D(9, 0, 0), QVector3D(6, 3, 4), QVector3D(0, 0, 0)
        ))
        self._parts.append(BuildingPart(
            plane_mesh, self._wood_color,
            QVector3D(9, -0.3, 2.01), QVector3D(5, 2.5, 1), QVector3D(0, 0, 0),
            self._garage_texture
        ))

        # Крыша крыльца
        self._parts.append(BuildingPart(
            cube_mesh, self._brick_color,
            QVector3D(4.5, 1.5, 1.5), QVector3D(4, 0.3, 2), QVector3D(0, 0, 0),
            self._brick_texture
        ))

        # Окна первого этажа
        self._parts.append(BuildingPart(
            plane_mesh, self._window_color,
            QVector3D(0, 0, 2.01), QVector3D(5, 2, 1), QVector3D(0, 0, 0),
            self._window_texture
        ))
        self._parts.append(BuildingPart(
            plane_mesh, self._window_color,
            QVector3D(-3.01, 0, -2), QVector3D(5, 2, 1), QVector3D(0, -90, 0),
            self._window_texture
        ))

        # Дверь
        self._parts.append(BuildingPart(
            plane_mesh, self._wood_color,
            QVector3D(4.5, 0, 0.51), QVector3D(1.5, 2.5, 1), QVector3D(0, 0, 0),
            self._door_texture
        ))
        self._parts.append(BuildingPart(
            cube_mesh, self._brick_color,
            QVector3D(4.5, -1.5, 1.5), QVector3D(4, 0.3, 2), QVector3D(0, 0, 0),
            self._brick_texture
        ))

        # Земля
        self._parts.append(BuildingPart(
            plane_mesh, self._ground_color,
            QVector3D(0, -1.5, 0), QVector3D(50, 50, 1), QVector3D(-90, 0, 0),
            self._terrain_texture, self._terrain_second_texture
        ))

        # Первый этаж
        self._parts.append(BuildingPart(
            cube_mesh, self._brick_color,
            QVector3D(0, 0, 0), QVector3D(6, 3, 4), QVector3D(0, 0, 0),
            self._brick_texture
        ))
        self._parts.append(BuildingPart(
            cube_mesh, self._brick_color,
            QVector3D(0, 0, -4), QVector3D(6, 3, 4), QVector3D(0, 0, 0),
            self._brick_texture
        ))
        self._parts.append(BuildingPart(
            cube_mesh, self._brick_color,
            QVector3D(4, 0, -4), QVector3D(6, 3, 4), QVector3D(0, 0, 0),
            self._brick_texture
        ))
        self._parts.append(BuildingPart(
            cube_mesh, self._brick_color,
            QVector3D(9, 0, -4), QVector3D(6, 3, 4), QVector3D(0, 0, 0),
            self._brick_texture
        ))
        self._parts.append(BuildingPart(
            cube_mesh, self._brick_color,
            QVector3D(4.5, 0, -1), QVector3D(3, 3, 3), QVector3D(0, 0, 0)
        ))

    def create_cube_mesh(self):
        vertices = [
            # Позиции(X,Y,Z)   Нормали(NX,NY,NZ)  Цвет(R,G,B)  Текстурные координаты(U,V)
            # Передняя грань
            -0.5, -0.5, 0.5, 0, 0, 1, 1, 1, 1, 0, 0,
            0.5, -0.5, 0.5, 0, 0, 1, 1, 1, 1, 1, 0,
            0.5, 0.5, 0.5, 0, 0, 1, 1, 1, 1, 1, 1,
            -0.5, 0.5, 0.5, 0, 0, 1, 1, 1, 1, 0, 1,

            # Задняя грань
            -0.5, -0.5, -0.5, 0, 0, -1, 1, 1, 1, 1, 0,
            0.5, -0.5, -0.5, 0, 0, -1, 1, 1, 1, 0, 0,
            0.5, 0.5, -0.5, 0, 0, -1, 1, 1, 1, 0, 1,
            -0.5, 0.5, -0.5, 0, 0, -1, 1, 1, 1, 1, 1,

            # Левая грань
            -0.5, -0.5, -0.5, -1, 0, 0, 1, 1, 1, 0, 0,
            -0.5, -0.5, 0.5, -1, 0, 0, 1, 1, 1, 1, 0,
            -0.5, 0.5, 0.5, -1, 0, 0, 1, 1, 1, 1, 1,
            -0.5, 0.5, -0.5, -1, 0, 0, 1, 1, 1, 0, 1,

            # Правая грань
            0.5, -0.5, -0.5, 1, 0, 0, 1, 1, 1, 1, 0,
            0.5, -0.5, 0.5, 1, 0, 0, 1, 1, 1, 0, 0,
            0.5, 0.5, 0.5, 1, 0, 0, 1, 1, 1, 0, 1,
            0.5, 0.5, -0.5, 1, 0, 0, 1, 1, 1, 1, 1,

            # Верхняя грань
            -0.5, 0.5, -0.5, 0, 1, 0, 1, 1, 1, 0, 1,
            0.5, 0.5, -0.5, 0, 1, 0, 1, 1, 1, 1, 1,
            0.5, 0.5, 0.5, 0, 1, 0, 1, 1, 1, 1, 0,
            -0.5, 0.5, 0.5, 0, 1, 0, 1, 1, 1, 0, 0,

            # Нижняя грань
            -0.5, -0.5, -0.5, 0, -1, 0, 1, 1, 1, 1, 1,
            0.5, -0.5, -0.5, 0, -1, 0, 1, 1, 1, 0, 1,
            0.5, -0.5, 0.5, 0, -1, 0, 1, 1, 1, 0, 0,
            -0.5, -0.5, 0.5, 0, -1, 0, 1, 1, 1, 1, 0
        ]

        indices = [
            0, 1, 2, 2, 3, 0,  # Передняя
            6, 5, 4, 4, 7, 6,  # Задняя
            8, 9, 10, 10, 11, 8,  # Левая
            14, 13, 12, 12, 15, 14,  # Правая
            18, 17, 16, 16, 19, 18,  # Верхняя
            20, 21, 22, 22, 23, 20  # Нижняя
        ]

        return Mesh(vertices, indices)

    def create_plane_mesh(self):
        vertices = [
            -0.5, -0.5, 0, 0, 0, 1, 1, 1, 1, 0, 0,
            0.5, -0.5, 0, 0, 0, 1, 1, 1, 1, 1, 0,
            0.5, 0.5, 0, 0, 0, 1, 1, 1, 1, 1, 1,
            -0.5, 0.5, 0, 0, 0, 1, 1, 1, 1, 0, 1,
        ]

        indices = [0, 1, 3, 1, 2, 3]

        return Mesh(vertices, indices)

    def create_roof_mesh(self):
        vertices = [
            # Левая сторона
            0.0, 0.0, 0.0, -1, 1, 0, 1, 1, 1,
            2.5, 2.0, -2.0, -1, 1, 0, 1, 1, 1,
            0.0, 0.0, -4.0, -1, 1, 0, 1, 1, 1,

            # Правая сторона
            5.0, 0.0, 0.0, 1, 1, 0, 1, 1, 1,
            2.5, 2.0, -2.0, 1, 1, 0, 1, 1, 1,
            5.0, 0.0, -4.0, 1, 1, 0, 1, 1, 1,

            # Передняя сторона
            0.0, 0.0, 0.0, 0, 1, 1, 1, 1, 1,
            2.5, 2.0, -2.0, 0, 1, 1, 1, 1, 1,
            5.0, 0.0, 0.0, 0, 1, 1, 1, 1, 1,

            # Задняя сторона
            0.0, 0.0, -4.0, 0, 1, -1, 1, 1, 1,
            2.5, 2.0, -2.0, 0, 1, -1, 1, 1, 1,
            5.0, 0.0, -4.0, 0, 1, -1, 1, 1, 1
        ]

        indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

        return Mesh(vertices, indices)

    def draw(self, shader):
        for part in self._parts:
            part.draw(shader)