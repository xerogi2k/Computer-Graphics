import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from CottageWindow import CottageWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("MainWindow created")  # ОТЛАДКА

        self.setWindowTitle("Реалистичный коттедж с прилегающими постройками")
        self.resize(1280, 720)
        self.setMinimumSize(800, 600)

        # Создаем и устанавливаем OpenGL виджет
        print("Creating CottageWindow...")  # ОТЛАДКА
        self.cottage_widget = CottageWindow()
        self.setCentralWidget(self.cottage_widget)

        print("MainWindow setup complete")  # ОТЛАДКА


def main():
    print("Starting application...")  # ОТЛАДКА

    # Создаем приложение Qt
    app = QApplication(sys.argv)

    # Создаем главное окно
    main_window = MainWindow()

    # Показываем окно
    main_window.show()
    print("Window shown")  # ОТЛАДКА

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()