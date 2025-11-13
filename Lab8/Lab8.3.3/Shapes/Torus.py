import numpy as np
import math
from Models.Ray import Ray
from Models.IntersectionResult import IntersectionResult
from Models.Material import Material
from Shapes.Interfaces.IShape import IShape
from MathUtils import dot, normalize, vector3


class Torus(IShape):
    def __init__(self, center=None, major_radius=1.0, minor_radius=0.3,
                 material=None, color=None):
        self.center = center if center is not None else np.zeros(3, dtype=np.float32)
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.material = material if material is not None else Material()
        self.color = color if color is not None else np.zeros(3, dtype=np.float32)

    # Свойства для совместимости с C#
    @property
    def Center(self):
        return self.center

    @Center.setter
    def Center(self, value):
        self.center = value

    @property
    def MajorRadius(self):
        return self.major_radius

    @MajorRadius.setter
    def MajorRadius(self, value):
        self.major_radius = value

    @property
    def MinorRadius(self):
        return self.minor_radius

    @MinorRadius.setter
    def MinorRadius(self, value):
        self.minor_radius = value

    @property
    def Color(self):
        return self.color

    @Color.setter
    def Color(self, value):
        self.color = value

    @property
    def Material(self):
        return self.material

    @Material.setter
    def Material(self, value):
        self.material = value

    def intersect(self, ray: Ray) -> IntersectionResult:
        result = IntersectionResult()

        local_origin = ray.origin - self.center

        ox, oy, oz = local_origin
        dx, dy, dz = ray.direction
        R = self.major_radius
        r = self.minor_radius
        R2 = R * R
        r2 = r * r

        # Уравнение тора
        sum_d_sq = dx * dx + dy * dy + dz * dz
        sum_o_sq = ox * ox + oy * oy + oz * oz
        sum_od = ox * dx + oy * dy + oz * dz
        sum_o_sq_minus = sum_o_sq - R2 - r2

        A = sum_d_sq * sum_d_sq
        B = 4 * sum_d_sq * sum_od
        C = 2 * sum_d_sq * sum_o_sq_minus + 4 * sum_od * sum_od + 4 * R2 * dy * dy
        D = 4 * sum_od * sum_o_sq_minus + 8 * R2 * oy * dy
        E = sum_o_sq_minus * sum_o_sq_minus - 4 * R2 * (r2 - oy * oy)

        roots = self._solve_quartic_optimized(A, B, C, D, E)

        closest_t = None
        for t in roots:
            if t > 0.001 and (closest_t is None or t < closest_t):
                closest_t = t

        if closest_t is not None:
            point = local_origin + ray.direction * closest_t
            world_point = point + self.center
            normal = self._calculate_normal(point)

            result.point = world_point
            result.distance = closest_t
            result.normal = normal
            result.color = self.color
            result.material = self.material
            result.shape = self

        return result

    def _solve_quartic_optimized(self, a, b, c, d, e):
        roots = []

        # Уменьшаем количество шагов
        steps = 100
        max_t = 20.0

        prev_value = self._quartic_function(a, b, c, d, e, 0)

        for i in range(1, steps + 1):
            t = i * max_t / steps
            value = self._quartic_function(a, b, c, d, e, t)

            if prev_value * value <= 0:
                root = self._refine_root_optimized(a, b, c, d, e, t - max_t / steps, t)
                if abs(self._quartic_function(a, b, c, d, e, root)) < 0.01:
                    roots.append(root)

            prev_value = value

        return roots

    def _refine_root_optimized(self, a, b, c, d, e, t1, t2):
        iterations = 5
        mid = (t1 + t2) * 0.5

        for i in range(iterations):
            mid = (t1 + t2) * 0.5
            value = self._quartic_function(a, b, c, d, e, mid)

            if abs(value) < 0.001:
                return mid

            if self._quartic_function(a, b, c, d, e, t1) * value < 0:
                t2 = mid
            else:
                t1 = mid

        return mid

    def _quartic_function(self, a, b, c, d, e, t):
        return a * t * t * t * t + b * t * t * t + c * t * t + d * t + e

    def _calculate_normal(self, p):
        x, y, z = p
        R = self.major_radius
        r = self.minor_radius
        temp = x * x + y * y + z * z - R * R - r * r

        nx = 4 * x * temp
        ny = 4 * y * temp - 4 * R * R * y
        nz = 4 * z * temp

        normal = vector3(nx, ny, nz)
        return normalize(normal)