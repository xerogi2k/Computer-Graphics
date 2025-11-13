import sys
from PySide6.QtWidgets import QApplication
from Window import MainWindow


def main():
    print("Запуск шахматного приложения...")

    # Создаем приложение Qt
    app = QApplication(sys.argv)

    # Создаем главное окно
    main_window = MainWindow()

    # Показываем окно
    main_window.show()

    print("Приложение запущено успешно!")

    # Запускаем главный цикл приложения
    sys.exit(app.exec())

if __name__ == "__main__":
    main()