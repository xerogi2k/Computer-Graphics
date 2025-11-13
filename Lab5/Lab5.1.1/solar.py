import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import math
import pyrr
from PIL import Image
from abc import ABC, abstractmethod
from typing import Tuple

# Константы для размера окна
WINDOW_W = 1280
WINDOW_H = 800


# Класс для работы с шейдерной программой
class ShaderProgram:
    VERTEX_SHADER = """
    #version 330 core
    layout(location = 0) in vec3 aPos;
    layout(location = 1) in vec3 aNormal;
    layout(location = 2) in vec2 aUV;

    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;

    out vec3 FragPos;
    out vec3 Normal;
    out vec2 UV;

    void main()
    {
        vec4 worldPos = model * vec4(aPos,1.0);
        FragPos = worldPos.xyz;
        Normal = mat3(transpose(inverse(model))) * aNormal;
        UV = aUV;
        gl_Position = projection * view * worldPos;
    }
    """

    FRAGMENT_SHADER = """
    #version 330 core
    in vec3 FragPos;
    in vec3 Normal;
    in vec2 UV;

    uniform sampler2D tex;
    uniform vec3 sunPos;
    uniform vec3 viewPos;
    uniform bool emissive;
    uniform float sunRadius;

    out vec4 FragColor;

    void main()
    {
        vec3 albedo = texture(tex, UV).rgb;
        if (emissive)
        {
            FragColor = vec4(albedo*5.0,1.0);
            return;
        }

        // Точечный источник света от Солнца
        vec3 toSun = sunPos - FragPos;
        float distanceToSun = length(toSun);
        vec3 L = normalize(toSun);

        // Затухание света с расстоянием
        float attenuation = 1.0 / (0.1 * distanceToSun + 0.001 * distanceToSun * distanceToSun);

        vec3 ambient = 0.1 * albedo;
        vec3 N = normalize(Normal);
        float diff = max(dot(N, L), 0.0);
        vec3 diffuse = diff * albedo * attenuation;

        vec3 V = normalize(viewPos - FragPos);
        vec3 H = normalize(L + V);
        float spec = pow(max(dot(N, H), 0.0), 32.0);
        vec3 specular = vec3(1.0) * spec * 0.3 * attenuation;

        vec3 result = ambient + diffuse + specular;
        result = result / (result + vec3(1.0));
        FragColor = vec4(result, 1.0);
    }
    """

    def __init__(self):
        self.program = self._compile_program()
        self._setup_uniform_locations()

    # Компилирует и возвращает шейдерную программу
    def _compile_program(self) -> int:
        program = compileProgram(
            compileShader(self.VERTEX_SHADER, GL_VERTEX_SHADER),
            compileShader(self.FRAGMENT_SHADER, GL_FRAGMENT_SHADER),
            validate=False
        )
        # Валидация программы
        tmp_vao = glGenVertexArrays(1)
        glBindVertexArray(tmp_vao)
        glValidateProgram(program)
        glBindVertexArray(0)

        return program

    # Получает локации uniform переменных
    def _setup_uniform_locations(self):
        self.loc_view = glGetUniformLocation(self.program, "view")
        self.loc_proj = glGetUniformLocation(self.program, "projection")
        self.loc_model = glGetUniformLocation(self.program, "model")
        self.loc_sunPos = glGetUniformLocation(self.program, "sunPos")
        self.loc_viewPos = glGetUniformLocation(self.program, "viewPos")
        self.loc_emissive = glGetUniformLocation(self.program, "emissive")
        self.loc_sunRadius = glGetUniformLocation(self.program, "sunRadius")

    # Активирует шейдерную программу
    def use(self):
        glUseProgram(self.program)

    # Устанавливает матрицу вида
    def set_view_matrix(self, matrix: np.ndarray):
        glUniformMatrix4fv(self.loc_view, 1, GL_FALSE, matrix)
    # Устанавливает матрицу проекции
    def set_projection_matrix(self, matrix: np.ndarray):
        glUniformMatrix4fv(self.loc_proj, 1, GL_FALSE, matrix)
    # Устанавливает матрицу модели
    def set_model_matrix(self, matrix: np.ndarray):
        glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, matrix)
    # Устанавливает позицию солнца
    def set_sun_position(self, position: Tuple[float, float, float]):
        glUniform3f(self.loc_sunPos, *position)
    # Устанавливает позицию камеры
    def set_view_position(self, position: Tuple[float, float, float]):
        glUniform3fv(self.loc_viewPos, 1, position)
    # Устанавливает флаг эмиссии
    def set_emissive(self, is_emissive: bool):
        glUniform1i(self.loc_emissive, GL_TRUE if is_emissive else GL_FALSE)
    # Устанавливает радиус солнца
    def set_sun_radius(self, radius: float):
        glUniform1f(self.loc_sunRadius, radius)

# Класс для работы с 3D мэшем
class Mesh:
    def __init__(self, positions: np.ndarray, normals: np.ndarray,
                 uvs: np.ndarray, indices: np.ndarray):
        self.positions = positions
        self.normals = normals
        self.uvs = uvs
        self.indices = indices
        self.vao, self.index_count = self._create_vao()

    @classmethod
    # Создает UV-сферу
    def create_uv_sphere(cls, latitude_segments: int = 64, longitude_segments: int = 64) -> 'Mesh':
        positions = []
        normals = []
        uvs = []
        indices = []

        for i in range(latitude_segments + 1):
            theta = math.pi * i / latitude_segments
            sin_t = math.sin(theta)
            cos_t = math.cos(theta)
            for j in range(longitude_segments + 1):
                phi = 2 * math.pi * j / longitude_segments
                x = sin_t * math.cos(phi)
                y = cos_t
                z = sin_t * math.sin(phi)
                positions.extend([x, y, z])
                normals.extend([x, y, z])
                uvs.extend([j / longitude_segments, 1 - i / latitude_segments])

        for i in range(latitude_segments):
            for j in range(longitude_segments):
                p1 = i * (longitude_segments + 1) + j
                p2 = p1 + (longitude_segments + 1)
                indices.extend([p1, p2, p1 + 1])
                indices.extend([p1 + 1, p2, p2 + 1])

        return cls(
            np.array(positions, dtype=np.float32),
            np.array(normals, dtype=np.float32),
            np.array(uvs, dtype=np.float32),
            np.array(indices, dtype=np.uint32)
        )
    # Создает Vertex Array Object
    def _create_vao(self) -> Tuple[int, int]:
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        # Позиции
        vbo_pos = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, self.positions.nbytes, self.positions, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Нормали
        vbo_norm = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_norm)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        # UV координаты
        vbo_uv = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_uv)
        glBufferData(GL_ARRAY_BUFFER, self.uvs.nbytes, self.uvs, GL_STATIC_DRAW)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)

        # Индексы
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        glBindVertexArray(0)
        return vao, self.indices.size
    # Отрисовывает мэш
    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

# Класс для работы с текстурами
class Texture:

    def __init__(self, path: str, fallback_color: Tuple[int, int, int] = (128, 128, 128)):
        self.texture_id = self._load_texture(path, fallback_color)
    # Загружает текстуру из файла
    def _load_texture(self, path: str, fallback_color: Tuple[int, int, int]) -> int:
        try:
            img = Image.open(path).convert('RGB')
        except:
            img = Image.new('RGB', (1024, 1024), color=fallback_color)

        data = np.array(img, dtype=np.uint8)
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        return tex
    # Активирует текстуру
    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

# Класс для управления камерой
class Camera:

    def __init__(self):
        self.yaw = 0.0
        self.pitch = 0.2
        self.distance = 15.0
        self.last_x = 0
        self.last_y = 0
        self.mouse_left_down = False
    # Возвращает позицию камеры
    def get_position(self) -> np.ndarray:
        cam_x = math.cos(self.yaw) * math.cos(self.pitch) * self.distance
        cam_y = math.sin(self.pitch) * self.distance
        cam_z = math.sin(self.yaw) * math.cos(self.pitch) * self.distance
        return np.array([cam_x, cam_y, cam_z], dtype=np.float32)
    # Возвращает матрицу вида
    def get_view_matrix(self) -> np.ndarray:
        camera_pos = self.get_position()
        return pyrr.matrix44.create_look_at(camera_pos, [0, 0, 0], [0, 1, 0])
    # Обрабатывает движение мыши
    def handle_mouse_move(self, xpos: float, ypos: float):
        if not self.mouse_left_down:
            self.last_x = xpos
            self.last_y = ypos
            return

        dx = xpos - self.last_x
        dy = ypos - self.last_y
        self.last_x = xpos
        self.last_y = ypos

        sensitivity = 0.005
        self.yaw += dx * sensitivity
        self.pitch += dy * sensitivity
        self.pitch = max(-math.pi / 2 + 0.01, min(math.pi / 2 - 0.01, self.pitch))
    # Обрабатывает нажатия кнопок мыши
    def handle_mouse_button(self, button: int, action: int):
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.mouse_left_down = action == glfw.PRESS
    # Обрабатывает прокрутку колесика мыши
    def handle_scroll(self, yoffset: float):
        self.distance *= (0.9 ** yoffset)
        self.distance = max(3.0, min(60.0, self.distance))


# КЛАССЫ НЕБЕСНЫХ ТЕЛ

#Абстрактный базовый класс для небесных тел
class CelestialBody(ABC):

    def __init__(self, radius: float, texture_path: str, fallback_color: Tuple[int, int, int]):
        self.radius = radius
        self.texture = Texture(texture_path, fallback_color)
        self.mesh = Mesh.create_uv_sphere()

    @abstractmethod
    # Возвращает матрицу модели для текущего времени
    def get_model_matrix(self, time: float) -> np.ndarray:
        pass
    # Отрисовывает небесное тело
    def draw(self, shader: ShaderProgram, time: float, is_emissive: bool = False):
        model_matrix = self.get_model_matrix(time)
        shader.set_model_matrix(model_matrix)
        shader.set_emissive(is_emissive)
        self.texture.bind()
        self.mesh.draw()

# Класс Солнца
class Sun(CelestialBody):

    def __init__(self):
        super().__init__(
            radius=1.5,
            texture_path="textures/sun.jpg",
            fallback_color=(255, 180, 50)
        )
    # Солнце статично в центре системы
    def get_model_matrix(self, time: float) -> np.ndarray:
        return pyrr.matrix44.create_from_scale([self.radius] * 3)

# Класс планеты с орбитальным движением
class Planet(CelestialBody):

    def __init__(self, radius: float, orbit_radius: float, orbit_speed: float,
                 spin_speed: float, axial_tilt_deg: float, texture_path: str,
                 fallback_color: Tuple[int, int, int]):
        super().__init__(radius, texture_path, fallback_color)
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed
        self.spin_speed = spin_speed
        self.axial_tilt_rad = math.radians(axial_tilt_deg)
    # Вычисляет матрицу модели с учетом орбиты и вращения
    def get_model_matrix(self, time: float) -> np.ndarray:
        # Орбитальное движение
        orbit_angle = self.orbit_speed * time
        x = math.cos(orbit_angle) * self.orbit_radius
        z = math.sin(orbit_angle) * self.orbit_radius

        # Создание матрицы модели
        model = pyrr.matrix44.create_from_scale([self.radius] * 3)  # Масштаб
        model = pyrr.matrix44.multiply(model, pyrr.matrix44.create_from_y_rotation(self.spin_speed * time))  # Вращение
        model = pyrr.matrix44.multiply(model, pyrr.matrix44.create_from_x_rotation(self.axial_tilt_rad))  # Наклон оси
        model = pyrr.matrix44.multiply(model, pyrr.matrix44.create_from_translation([0.6 * x, 0, 0.6 * z]))  # Позиция на орбите

        return model

# Класс Луны с синхронным вращением и движением относительно Земли
class Moon(CelestialBody):

    def __init__(self, earth_planet: Planet):
        super().__init__(
            radius=0.18,
            texture_path="textures/moon.jpg",
            fallback_color=(180, 180, 180)
        )
        self.earth = earth_planet
        self.orbit_radius = 1.4
        self.orbit_speed = 3.0
    # Вычисляет матрицу модели Луны с учетом движения относительно Земли
    def get_model_matrix(self, time: float) -> np.ndarray:
        # Орбитальное движение Луны относительно Земли
        moon_orbit_angle = self.orbit_speed * time
        moon_relative_x = math.cos(moon_orbit_angle) * self.orbit_radius
        moon_relative_z = math.sin(moon_orbit_angle) * self.orbit_radius

        # Вычисляем позицию Земли напрямую (аналогично методу в Planet)
        earth_orbit_angle = self.earth.orbit_speed * time
        earth_x = math.cos(earth_orbit_angle) * self.earth.orbit_radius
        earth_z = math.sin(earth_orbit_angle) * self.earth.orbit_radius

        # Позиция Луны = позиция Земли + относительное смещение
        moon_x = earth_x + moon_relative_x
        moon_z = earth_z + moon_relative_z

        # Синхронное вращение (всегда одной стороной к Земле)
        model = pyrr.matrix44.create_from_y_rotation(-moon_orbit_angle)  # Вращение синхронно с орбитой
        model = pyrr.matrix44.multiply(model, pyrr.matrix44.create_from_translation([3.33 * moon_x, 0, 3.33 * moon_z]))
        model = pyrr.matrix44.multiply(model, pyrr.matrix44.create_from_scale([self.radius] * 3))

        return model

# Класс солнечной системы, управляющий всеми небесными телами
class SolarSystem:

    def __init__(self):
        # Сначала создаем Землю
        self.earth = Planet(
            radius=0.6,
            orbit_radius=6.0,
            orbit_speed=0.5,
            spin_speed=1.5,
            axial_tilt_deg=23.43,
            texture_path="textures/earth.jpg",
            fallback_color=(30, 90, 180)
        )

        # Затем создаем Луну, передавая ссылку на Землю
        self.moon = Moon(self.earth)

        self.bodies = {
            'sun': Sun(),
            'earth': self.earth,
            'moon': self.moon
        }
    # Отрисовывает все небесные тела
    def draw(self, shader: ShaderProgram, time: float):
        # Солнце (эмиссивное)
        self.bodies['sun'].draw(shader, time, is_emissive=True)

        # Планеты и спутники (не эмиссивные)
        self.bodies['earth'].draw(shader, time, is_emissive=False)
        self.bodies['moon'].draw(shader, time, is_emissive=False)

# ГЛАВНЫЙ КЛАСС ПРИЛОЖЕНИЯ

# Главный класс приложения солнечной системы
class SolarSystemApp:

    def __init__(self):
        self.window = None
        self.shader = None
        self.camera = Camera()
        self.solar_system = None
        self.start_time = 0.0
    # Инициализирует приложение
    def initialize(self) -> bool:
        if not glfw.init():
            return False

        # Настройка окна
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(WINDOW_W, WINDOW_H, "Solar System", None, None)
        if not self.window:
            glfw.terminate()
            return False

        glfw.make_context_current(self.window)

        # Настройка callback'ов
        glfw.set_cursor_pos_callback(self.window, self._cursor_pos_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_btn_callback)
        glfw.set_scroll_callback(self.window, self._scroll_callback)
        glfw.set_framebuffer_size_callback(self.window, self._framebuffer_size_callback)

        # Настройка OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # Инициализация компонентов
        self.shader = ShaderProgram()
        self.solar_system = SolarSystem()
        self.start_time = glfw.get_time()

        # Начальная настройка
        self._setup_initial_state()

        return True
    # Устанавливает начальное состояние шейдеров
    def _setup_initial_state(self):
        self.shader.use()
        self.shader.set_sun_position((0.0, 0.0, 0.0))
        self.shader.set_sun_radius(1.5)

        # Установка проекционной матрицы
        width, height = glfw.get_framebuffer_size(self.window)
        self._framebuffer_size_callback(self.window, width, height)
    # Callback для движения мыши
    def _cursor_pos_callback(self, window, xpos: float, ypos: float):
        self.camera.handle_mouse_move(xpos, ypos)
    # Callback для нажатий кнопок мыши
    def _mouse_btn_callback(self, window, button: int, action: int, mods: int):
        self.camera.handle_mouse_button(button, action)
    # Callback для прокрутки колесика мыши
    def _scroll_callback(self, window, xoffset: float, yoffset: float):
        self.camera.handle_scroll(yoffset)
    # Callback для изменения размера окна
    def _framebuffer_size_callback(self, window, width: int, height: int):
        glViewport(0, 0, width, height)
        if width > 0 and height > 0:
            proj = pyrr.matrix44.create_perspective_projection(45, width / height, 0.1, 200.0)
            self.shader.use()
            self.shader.set_projection_matrix(proj)
    # апускает главный цикл приложения
    def run(self):
        if not self.initialize():
            return

        while not glfw.window_should_close(self.window):
            self._render_frame()
            glfw.swap_buffers(self.window)
            glfw.poll_events()

        self.cleanup()
    # Отрисовывает один кадр
    def _render_frame(self):
        # Очистка экрана
        glClearColor(0.02, 0.03, 0.06, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Расчет времени
        current_time = glfw.get_time() - self.start_time

        # Активация шейдера
        self.shader.use()

        # Обновление камеры
        camera_pos = self.camera.get_position()
        view_matrix = self.camera.get_view_matrix()

        self.shader.set_view_matrix(view_matrix)
        self.shader.set_view_position(camera_pos)

        # Отрисовка солнечной системы
        self.solar_system.draw(self.shader, current_time)
    # Очищает ресурсы
    def cleanup(self):
        glfw.terminate()


# ТОЧКА ВХОДА

#Точка входа в приложение
def main():
    app = SolarSystemApp()
    app.run()


if __name__ == "__main__":
    main()