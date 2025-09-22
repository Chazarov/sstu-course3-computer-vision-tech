"""
Доменные модели для приложения обработки изображений.
Содержат бизнес-логику и основные сущности.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from enum import Enum
import numpy as np


class ColorModel(Enum):
    """Цветовые модели изображения"""
    RGB = "RGB"
    RGBA = "RGBA"
    GRAYSCALE = "L"
    CMYK = "CMYK"
    LAB = "LAB"
    HSV = "HSV"


class ImageFormat(Enum):
    """Форматы изображений"""
    JPEG = "JPEG"
    PNG = "PNG"
    BMP = "BMP"
    TIFF = "TIFF"
    GIF = "GIF"
    WEBP = "WEBP"
    OTHER = "OTHER"


@dataclass
class ImageInfo:
    """Информация об изображении"""
    file_size: int  # размер в байтах
    width: int
    height: int
    color_depth: int
    format: ImageFormat
    color_model: ColorModel
    exif_data: Dict[str, Any]
    additional_info: Dict[str, Any]
    
    @property
    def resolution(self) -> Tuple[int, int]:
        """Разрешение изображения"""
        return (self.width, self.height)
    
    @property
    def file_size_mb(self) -> float:
        """Размер файла в МБ"""
        return self.file_size / (1024 * 1024)


@dataclass
class Histogram:
    """Гистограмма изображения"""
    red_channel: Optional[np.ndarray] = None
    green_channel: Optional[np.ndarray] = None
    blue_channel: Optional[np.ndarray] = None
    grayscale: Optional[np.ndarray] = None
    
    def has_color_channels(self) -> bool:
        """Проверяет наличие цветных каналов"""
        return all([
            self.red_channel is not None,
            self.green_channel is not None,
            self.blue_channel is not None
        ])


@dataclass
class ImageProcessingParameters:
    """Параметры обработки изображения"""
    brightness: float = 0.0  # от -100 до 100
    contrast: float = 1.0    # от 0.0 до 3.0
    saturation: float = 1.0  # от 0.0 до 3.0
    rotation: int = 0        # 0, 90, 180, 270 градусов
    
    def validate(self) -> bool:
        """Валидация параметров"""
        return (
            -100 <= self.brightness <= 100 and
            0.0 <= self.contrast <= 3.0 and
            0.0 <= self.saturation <= 3.0 and
            self.rotation in [0, 90, 180, 270]
        )


class Image:
    """Основная доменная модель изображения"""
    
    def __init__(self, file_path: str, image_data: np.ndarray, info: ImageInfo):
        self._file_path = file_path
        self._original_data = image_data.copy()
        self._current_data = image_data.copy()
        self._info = info
        self._is_modified = False
    
    @property
    def file_path(self) -> str:
        return self._file_path
    
    @property
    def info(self) -> ImageInfo:
        return self._info
    
    @property
    def original_data(self) -> np.ndarray:
        return self._original_data.copy()
    
    @property
    def current_data(self) -> np.ndarray:
        return self._current_data.copy()
    
    @property
    def is_modified(self) -> bool:
        return self._is_modified
    
    def update_data(self, new_data: np.ndarray) -> None:
        """Обновляет данные изображения"""
        self._current_data = new_data.copy()
        self._is_modified = True
    
    def reset_to_original(self) -> None:
        """Сбрасывает изображение к оригиналу"""
        self._current_data = self._original_data.copy()
        self._is_modified = False
    
    def is_grayscale(self) -> bool:
        """Проверяет, является ли изображение черно-белым"""
        return len(self._current_data.shape) == 2 or self._info.color_model == ColorModel.GRAYSCALE
