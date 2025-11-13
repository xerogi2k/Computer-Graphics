import numpy as np
import math

def vector3(x=0.0, y=0.0, z=0.0):
    """Создает 3D вектор"""
    return np.array([x, y, z], dtype=np.float32)

def normalize(vector):
    """Нормализует вектор"""
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

def dot(v1, v2):
    """Скалярное произведение"""
    return np.dot(v1, v2)

def cross(v1, v2):
    """Векторное произведение"""
    return np.cross(v1, v2)

def reflect(incident, normal):
    """Отражение вектора incident от нормали normal"""
    return incident - 2 * dot(incident, normal) * normal

def length(vector):
    """Длина вектора"""
    return np.linalg.norm(vector)

def distance(v1, v2):
    """Расстояние между двумя точками"""
    return np.linalg.norm(v2 - v1)

def clamp(value, min_val, max_val):
    """Ограничивает значение диапазоном"""
    if isinstance(value, np.ndarray):
        return np.clip(value, min_val, max_val)
    return max(min_val, min(value, max_val))

def lerp(a, b, t):
    """Линейная интерполяция между a и b"""
    return a + (b - a) * t

def magnitude_squared(vector):
    """Квадрат длины вектора (более быстрый расчет)"""
    return dot(vector, vector)

def zero():
    """Нулевой вектор"""
    return vector3(0, 0, 0)

def one():
    """Вектор (1, 1, 1)"""
    return vector3(1, 1, 1)

def up():
    """Вектор вверх (0, 1, 0)"""
    return vector3(0, 1, 0)

def down():
    """Вектор вниз (0, -1, 0)"""
    return vector3(0, -1, 0)

def forward():
    """Вектор вперед (0, 0, -1)"""
    return vector3(0, 0, -1)

def back():
    """Вектор назад (0, 0, 1)"""
    return vector3(0, 0, 1)

def right():
    """Вектор вправо (1, 0, 0)"""
    return vector3(1, 0, 0)

def left():
    """Вектор влево (-1, 0, 0)"""
    return vector3(-1, 0, 0)