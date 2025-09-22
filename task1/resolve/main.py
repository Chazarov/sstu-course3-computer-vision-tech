"""
Главный модуль приложения для обработки изображений.
Настраивает зависимости и запускает приложение.
"""
import sys
import os

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.image_service import ImageService
from adapters.image_repository import PillowImageRepository, ExifReader
from adapters.image_processor import PillowImageProcessor
from adapters.histogram_service import MatplotlibHistogramService, PillowDisplayService
from adapters.file_dialog_service import FreeSimpleGUIFileDialogService
from presentation.gui import ImageProcessorGUI
from configs import Settings


class Application:
    """Главный класс приложения"""
    
    def __init__(self):
        self._settings = Settings()
        self._setup_dependencies()
    
    def _setup_dependencies(self) -> None:
        """Настраивает зависимости согласно принципам чистой архитектуры"""
        
        # Создаем адаптеры (внешний слой)
        exif_reader = ExifReader()
        image_repository = PillowImageRepository(exif_reader)
        image_processor = PillowImageProcessor()
        histogram_service = MatplotlibHistogramService()
        display_service = PillowDisplayService()
        file_dialog_service = FreeSimpleGUIFileDialogService()
        
        # Создаем сервисы (бизнес-логика)
        self._image_service = ImageService(
            image_repository=image_repository,
            image_processor=image_processor,
            histogram_service=histogram_service,
            display_service=display_service
        )
        
        # Создаем GUI (презентационный слой)
        self._gui = ImageProcessorGUI(
            image_service=self._image_service,
            file_dialog_service=file_dialog_service
        )
    
    def run(self) -> None:
        """Запускает приложение"""
        try:
            print("Запуск приложения для обработки изображений...")
            self._gui.run()
            print("Приложение завершено.")
            
        except Exception as e:
            print(f"Критическая ошибка приложения: {e}")
            sys.exit(1)


def main() -> None:
    """Точка входа в приложение"""
    try:
        app = Application()
        app.run()
        
    except KeyboardInterrupt:
        print("\\nПриложение прервано пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
