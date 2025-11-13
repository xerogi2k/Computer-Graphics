import numpy as np
import pygame
import math
from Models.Ray import Ray
from Models.IntersectionResult import IntersectionResult
from Models.Material import Material
from Scene import Scene
from AreaLight import AreaLight
from Shapes.ChessBoard import InfinityChessBoard
from Shapes.Torus import Torus
from MathUtils import dot, normalize, reflect, length, distance, clamp, vector3


class RayTracer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.max_depth = 2
        self.scene = self._create_scene()

    def _create_scene(self):
        """Создает сцену с тором и шахматной доской"""
        scene = Scene()

        # Материалы
        torus_material = Material(
            diffuse=vector3(0.8, 0.8, 0.8),
            specular=vector3(1.0, 1.0, 1.0),
            ambient=vector3(0.1, 0.1, 0.1),
            shininess=32.0
        )

        floor_material = Material(
            diffuse=vector3(0.8, 0.8, 0.8),
            specular=vector3(0.3, 0.3, 0.3),
            ambient=vector3(0.1, 0.1, 0.1),
            shininess=16.0
        )

        # Тор
        torus = Torus(
            center=vector3(0, 0, -3),
            major_radius=0.8,
            minor_radius=0.2,
            material=torus_material,
            color=vector3(0.7, 0.2, 0.2)  # Красный
        )
        scene.add(torus)

        # Шахматная доска
        chess_board = InfinityChessBoard(
            point=vector3(0, -1, 0),
            normal=vector3(0, 1, 0),
            material=floor_material,
            checker_size=1.0,
            color1=vector3(0.9, 0.9, 0.9),  # Белый
            color2=vector3(0.1, 0.1, 0.1)  # Черный
        )
        scene.add(chess_board)

        # Источник света
        light = AreaLight(
            position=vector3(3, 5, -4),
            size=2.0,
            samples=16
        )
        scene.add_light(light)

        return scene

    def render(self):
        """Рендерит сцену и возвращает Surface Pygame"""
        surface = pygame.Surface((self.width, self.height))
        pixels = pygame.surfarray.pixels3d(surface)

        camera_pos = vector3(0, 1, 3)
        total_pixels = self.width * self.height
        rendered_pixels = 0

        for y in range(self.height):
            for x in range(self.width):
                # Нормализуем координаты
                ndc_x = (2.0 * x / self.width) - 1.0
                ndc_y = 1.0 - (2.0 * y / self.height)

                # Направление луча через пиксель
                look_at = vector3(0, 0, -5)
                forward = normalize(look_at - camera_pos)
                right = vector3(1, 0, 0)
                up = vector3(0, 1, 0)

                ray_dir = normalize(forward + right * ndc_x + up * ndc_y)

                # Луч
                ray = Ray(camera_pos, ray_dir)

                color = self._trace_ray(ray)

                # Конвертируем в 0-255 и записываем в пиксель
                pixels[x, y] = (
                    int(clamp(color[0], 0, 1) * 255),
                    int(clamp(color[1], 0, 1) * 255),
                    int(clamp(color[2], 0, 1) * 255)
                )

                rendered_pixels += 1
                if rendered_pixels % 1000 == 0:
                    progress = (rendered_pixels / total_pixels) * 100
                    print(f"Rendered {rendered_pixels}/{total_pixels} pixels ({progress:.1f}%)")

        return surface

    def _trace_ray(self, ray: Ray, depth: int = 0) -> np.ndarray:
        """Трассирует луч и возвращает цвет"""
        if depth > 1:
            return vector3(0, 0, 0)  # Черный цвет для глубокой рекурсии

        intersection = self.scene.intersect(ray)

        # Фоновый цвет
        if not intersection.is_valid():  # Используем is_valid() вместо bool
            return vector3(0.3, 0.4, 0.5)  # Сине-голубой фон

        result = intersection
        material = result.material
        light = self.scene.lights[0] if self.scene.lights else None

        if not light:
            return result.color * material.ambient

        light_samples = light.get_samples_points()
        visible_samples = 0
        total_diffuse = vector3(0, 0, 0)
        total_specular = vector3(0, 0, 0)

        for light_sample in light_samples:
            # Луч от сэмпла до точки
            to_light = light_sample - result.point
            light_distance = length(to_light)
            light_dir = normalize(to_light)

            # Испускаем луч в сторону света из точки
            shadow_ray = Ray(result.point + result.normal * 0.001, light_dir)
            shadow_intersection = self.scene.intersect(shadow_ray)

            # Препятствие между точкой и светом
            if shadow_intersection.is_valid() and shadow_intersection.distance < light_distance:
                continue

            # Этот сэмпл видит свет
            visible_samples += 1

            # Диффузная компонента
            diffuse_intensity = max(0, dot(result.normal, light_dir))
            total_diffuse += result.color * material.diffuse * light.diffuse * diffuse_intensity

            # Зеркальная компонента
            view_dir = normalize(-ray.direction)
            reflect_dir = self._reflect(-light_dir, result.normal)
            spec_angle = max(0, dot(view_dir, reflect_dir))
            spec_intensity = math.pow(spec_angle, 32)

            total_specular += result.color * material.specular * light.specular * spec_intensity

        if visible_samples == 0:
            return result.color * light.ambient  # Полная тень

        # Коэффициент видимости = доля видимых сэмплов
        visibility = visible_samples / len(light_samples)

        # Усреднение освещения по видимым сэмплам
        diffuse = total_diffuse / visible_samples
        specular = total_specular / visible_samples
        ambient = result.color * light.ambient * material.ambient

        # Финальный цвет с учетом видимости
        final_color = (diffuse + specular) * visibility + ambient
        return clamp(final_color, 0, 1)

    def _reflect(self, vector: np.ndarray, normal: np.ndarray) -> np.ndarray:
        """Отражение вектора от нормали"""
        dot_product = dot(vector, normal)
        return vector - 2 * dot_product * normal