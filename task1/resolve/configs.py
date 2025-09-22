from pydantic_settings import BaseSettings
from typing import Tuple


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Настройки GUI
    window_title: str = "Обработка изображений"
    window_theme: str = "LightBlue3"
    max_image_display_size: Tuple[int, int] = (800, 600)
    
    # Настройки обработки изображений
    default_brightness: float = 0.0
    default_contrast: float = 1.0
    default_saturation: float = 1.0
    default_gamma: float = 1.0
    
    # Поддерживаемые форматы изображений
    supported_image_extensions: Tuple[str, ...] = (
        ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp"
    )
    
    # Настройки гистограммы
    histogram_bins: int = 256
    histogram_figure_size: Tuple[int, int] = (10, 6)
    histogram_dpi: int = 100
    
    class Config:
        env_prefix = "IMAGE_PROCESSOR_"

