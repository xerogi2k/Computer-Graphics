import os
from Model import Model


class ChessLoader:
    @staticmethod
    def load_chess(paths):
        models = []
        for path in paths:
            # Формируем полный путь к файлу
            full_path = os.path.join("Objects", path)
            try:
                model = Model(full_path)
                models.append(model)
                print(f"Successfully loaded: {full_path}")
            except Exception as e:
                print(f"Failed to load {full_path}: {e}")

        return models