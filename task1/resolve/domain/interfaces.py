"""
Интерфейсы для репозиториев и сервисов.
Определяют контракты для внешних зависимостей.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import numpy as np

from .models import Image, ImageInfo, Histogram, ImageProcessingParameters


class IImageRepository(ABC):
    """Интерфейс репозитория для работы с изображениями"""
    
    @abstractmethod
    def load_image(self, file_path: str) -> Optional[Image]:
        """Загружает изображение из файла"""
        pass
    
    @abstractmethod
    def save_image(self, image: Image, file_path: str) -> bool:
        """Сохраняет изображение в файл"""
        pass
    
    @abstractmethod
    def get_image_info(self, file_path: str) -> Optional[ImageInfo]:
        """Получает информацию об изображении"""
        pass


class IExifReader(ABC):
    """Интерфейс для чтения EXIF данных"""
    
    @abstractmethod
    def read_exif(self, file_path: str) -> Dict[str, Any]:
        """Читает EXIF данные из файла"""
        pass


class IImageProcessor(ABC):
    """Интерфейс для обработки изображений"""
    
    @abstractmethod
    def convert_to_grayscale(self, image_data: np.ndarray) -> np.ndarray:
        """Преобразует изображение в градации серого"""
        pass
    
    @abstractmethod
    def adjust_brightness(self, image_data: np.ndarray, brightness: float) -> np.ndarray:
        """Изменяет яркость изображения"""
        pass
    
    @abstractmethod
    def adjust_contrast(self, image_data: np.ndarray, contrast: float) -> np.ndarray:
        """Изменяет контрастность изображения"""
        pass
    
    @abstractmethod
    def adjust_saturation(self, image_data: np.ndarray, saturation: float) -> np.ndarray:
        """Изменяет насыщенность изображения"""
        pass
    
    @abstractmethod
    def rotate_image(self, image_data: np.ndarray, angle: int) -> np.ndarray:
        """Поворачивает изображение на заданный угол"""
        pass
    
    @abstractmethod
    def apply_linear_correction(self, image_data: np.ndarray, factor: float) -> np.ndarray:
        """Применяет линейную коррекцию к изображению"""
        pass
    
    @abstractmethod
    def apply_logarithmic_correction(self, image_data: np.ndarray, factor: float) -> np.ndarray:
        """Применяет логарифмическую коррекцию к изображению"""
        pass
    
    @abstractmethod
    def apply_gamma_correction(self, image_data: np.ndarray, gamma: float) -> np.ndarray:
        """Применяет гамма коррекцию к изображению"""
        pass


class IHistogramService(ABC):
    """Интерфейс сервиса для работы с гистограммами"""
    
    @abstractmethod
    def calculate_histogram(self, image_data: np.ndarray) -> Histogram:
        """Вычисляет гистограмму изображения"""
        pass
    
    @abstractmethod
    def plot_histogram(self, histogram: Histogram, title: str = "",  width: float = 10, height: float = 6) -> bytes:
        """Строит график гистограммы и возвращает его как байты"""
        pass


class IImageDisplayService(ABC):
    """Интерфейс сервиса для отображения изображений"""
    
    @abstractmethod
    def prepare_for_display(self, image_data: np.ndarray, max_size: Tuple[int, int] = (800, 600)) -> bytes:
        """Подготавливает изображение для отображения в GUI"""
        pass


class IFileDialogService(ABC):
    """Интерфейс сервиса для работы с диалогами файлов"""
    
    @abstractmethod
    def open_file_dialog(self, file_types: Tuple[Tuple[str, str], ...]) -> Optional[str]:
        """Открывает диалог выбора файла"""
        pass
    
    @abstractmethod
    def save_file_dialog(self, file_types: Tuple[Tuple[str, str], ...], default_extension: str = "") -> Optional[str]:
        """Открывает диалог сохранения файла"""
        pass
