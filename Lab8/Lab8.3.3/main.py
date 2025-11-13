import pygame
import sys
from RayTracer import RayTracer


def main():
    # Инициализация Pygame
    pygame.init()

    # Настройки окна
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Ray Tracing - Torus and Chess Board")

    # Создаем рендерер
    print("Initializing ray tracer...")
    ray_tracer = RayTracer(width, height)

    # Рендерим сцену
    print("Rendering scene...")
    image = ray_tracer.render()

    # Главный цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Отображаем рендер
        screen.blit(image, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()