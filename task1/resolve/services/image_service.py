"""
Сервисы для работы с изображениями.
Содержат бизнес-логику приложения.
"""
from typing import Optional, Tuple
import numpy as np

from domain.models import Image, ImageProcessingParameters, Histogram
from domain.interfaces import (
    IImageRepository, IImageProcessor, IHistogramService, 
    IImageDisplayService
)


class ImageService:
    """Основной сервис для работы с изображениями"""
    
    def __init__(
        self,
        image_repository: IImageRepository,
        image_processor: IImageProcessor,
        histogram_service: IHistogramService,
        display_service: IImageDisplayService
    ):
        self._image_repository = image_repository
        self._image_processor = image_processor
        self._histogram_service = histogram_service
        self._display_service = display_service
        self._current_image: Optional[Image] = None
        self._is_gray = False
        
        # Текущие параметры обработки для расчета дельты
        self._current_processing_params = ImageProcessingParameters()
        
        # Базовое изображение (с фильтрациями, но без параметров яркости/контрастности/насыщенности)
        self._base_image_data: Optional[np.ndarray] = None

    @property
    def current_image(self) -> Optional[Image]:
        """Получает текущее изображение"""
        return self._current_image
    
    def load_image(self, file_path: str) -> bool:
        """Загружает изображение"""
        try:
            image = self._image_repository.load_image(file_path)
            if image:
                self._current_image = image
                # Сбрасываем параметры обработки при загрузке нового изображения
                self._current_processing_params = ImageProcessingParameters()
                # Устанавливаем базовое изображение как оригинальное
                self._base_image_data = image.original_data.copy()
                self._is_gray = False
                return True
            return False
        except Exception:
            return False
    
    def save_image(self, file_path: str) -> bool:
        """Сохраняет текущее изображение"""
        if not self._current_image:
            return False
        
        try:
            return self._image_repository.save_image(self._current_image, file_path)
        except Exception:
            return False
    
    def convert_to_grayscale(self) -> bool:
        """Преобразует текущее изображение в градации серого"""
        if not self._current_image:
            return False
        
        try:
            grayscale_data = self._image_processor.convert_to_grayscale(
                self._current_image.current_data
            )
            self._current_image.update_data(grayscale_data)
            self._is_gray = True
            return True
        except Exception:
            return False
    
    def apply_processing_parameters(self, params: ImageProcessingParameters) -> bool:
        """Применяет параметры обработки к изображению"""
        if not self._current_image or not params.validate():
            return False
        
        if self._base_image_data is None:
            # Если базовое изображение не установлено, используем текущее
            self._base_image_data = self._current_image.current_data.copy()
        
        try:
            # Начинаем с базового изображения (с фильтрациями, но без параметров яркости/контрастности/насыщенности)
            processed_data = self._base_image_data.copy()
            
            # Применяем яркость
            if params.brightness != 0:
                processed_data = self._image_processor.adjust_brightness(
                    processed_data, params.brightness
                )
            
            # Применяем контрастность
            if params.contrast != 1.0:
                processed_data = self._image_processor.adjust_contrast(
                    processed_data, params.contrast
                )
            
            # Применяем насыщенность (только для цветных изображений)
            if not self._current_image.is_grayscale() and params.saturation != 1.0:
                processed_data = self._image_processor.adjust_saturation(
                    processed_data, params.saturation
                )
            
            # Для поворота применяем дельту и обновляем базовое изображение
            # так как это геометрическая трансформация
            rotation_delta = params.rotation - self._current_processing_params.rotation
            if rotation_delta != 0:
                # Поворачиваем обработанные данные
                processed_data = self._image_processor.rotate_image(
                    processed_data, rotation_delta
                )
                # Обновляем базовое изображение с поворотом
                self._base_image_data = self._image_processor.rotate_image(
                    self._base_image_data, rotation_delta
                )
            
            # Если изображение было в градациях серого, принудительно конвертируем результат
            if self._is_gray:
                processed_data = self._image_processor.convert_to_grayscale(processed_data)
            
            # Обновляем текущие параметры обработки
            self._current_processing_params = ImageProcessingParameters(
                brightness=params.brightness,
                contrast=params.contrast,
                saturation=params.saturation,
                rotation=params.rotation
            )
            
            self._current_image.update_data(processed_data)
            return True
        except Exception:
            return False
    
    def apply_linear_correction(self, factor: float) -> bool:
        """Применяет линейную коррекцию к изображению"""
        if not self._current_image:
            return False
        
        try:
            # Применяем к базовому изображению (или текущему, если базовое не установлено)
            base_data = self._base_image_data if self._base_image_data is not None else self._current_image.current_data
            
            corrected_data = self._image_processor.apply_linear_correction(
                base_data, factor
            )
            
            # Обновляем базовое изображение
            self._base_image_data = corrected_data.copy()
            
            # Переприменяем параметры яркости/контрастности/насыщенности к новому базовому изображению
            if self._current_processing_params.brightness != 0 or \
               self._current_processing_params.contrast != 1.0 or \
               self._current_processing_params.saturation != 1.0:
                self.apply_processing_parameters(self._current_processing_params)
            else:
                self._current_image.update_data(corrected_data)
            
            return True
        except Exception:
            return False
    
    def apply_logarithmic_correction(self, factor: float) -> bool:
        """Применяет логарифмическую коррекцию к изображению"""
        if not self._current_image:
            return False
        
        try:
            # Применяем к базовому изображению (или текущему, если базовое не установлено)
            base_data = self._base_image_data if self._base_image_data is not None else self._current_image.current_data
            
            corrected_data = self._image_processor.apply_logarithmic_correction(
                base_data, factor
            )
            
            # Обновляем базовое изображение
            self._base_image_data = corrected_data.copy()
            
            # Переприменяем параметры яркости/контрастности/насыщенности к новому базовому изображению
            if self._current_processing_params.brightness != 0 or \
               self._current_processing_params.contrast != 1.0 or \
               self._current_processing_params.saturation != 1.0:
                self.apply_processing_parameters(self._current_processing_params)
            else:
                self._current_image.update_data(corrected_data)
            
            return True
        except Exception:
            return False
    
    def apply_gamma_correction(self, gamma: float) -> bool:
        """Применяет гамма коррекцию к изображению"""
        if not self._current_image:
            return False
        
        try:
            # Применяем к базовому изображению (или текущему, если базовое не установлено)
            base_data = self._base_image_data if self._base_image_data is not None else self._current_image.current_data
            
            corrected_data = self._image_processor.apply_gamma_correction(
                base_data, gamma
            )
            
            # Обновляем базовое изображение
            self._base_image_data = corrected_data.copy()
            
            # Переприменяем параметры яркости/контрастности/насыщенности к новому базовому изображению
            if self._current_processing_params.brightness != 0 or \
               self._current_processing_params.contrast != 1.0 or \
               self._current_processing_params.saturation != 1.0:
                self.apply_processing_parameters(self._current_processing_params)
            else:
                self._current_image.update_data(corrected_data)
            
            return True
        except Exception:
            return False
    
    def get_histogram(self) -> Optional[Histogram]:
        """Получает гистограмму текущего изображения"""
        if not self._current_image:
            return None
        
        try:
            return self._histogram_service.calculate_histogram(
                self._current_image.current_data
            )
        except Exception:
            return None
    
    def get_original_histogram(self) -> Optional[Histogram]:
        """Получает гистограмму оригинального изображения"""
        if not self._current_image:
            return None
        
        try:
            return self._histogram_service.calculate_histogram(
                self._current_image.original_data
            )
        except Exception:
            return None
    
    def plot_histogram(self, histogram: Histogram, title: str = "", width: float = 10, height: float = 6) -> Optional[bytes]:
        """Строит график гистограммы"""
        try:
            return self._histogram_service.plot_histogram(histogram, title, width, height)
        except Exception:
            return None
    
    def prepare_image_for_display(self, max_size: Tuple[int, int] = (800, 600)) -> Optional[bytes]:
        """Подготавливает текущее изображение для отображения"""
        if not self._current_image:
            return None
        
        try:
            return self._display_service.prepare_for_display(
                self._current_image.current_data, max_size
            )
        except Exception:
            return None
    
    def reset_to_original(self) -> bool:
        """Сбрасывает изображение к оригиналу"""
        if not self._current_image:
            return False
        
        try:
            self._current_image.reset_to_original()
            self._is_gray = False
            # Сбрасываем параметры обработки
            self._current_processing_params = ImageProcessingParameters()
            # Сбрасываем базовое изображение
            self._base_image_data = self._current_image.original_data.copy()
            return True
        except Exception:
            return False
    
    def get_current_processing_params(self) -> ImageProcessingParameters:
        """Получает текущие параметры обработки"""
        return self._current_processing_params
    
    def reset_processing_params(self) -> bool:
        """Сбрасывает параметры обработки к значениям по умолчанию"""
        if not self._current_image:
            return False
        
        try:
            # Сбрасываем параметры обработки
            self._current_processing_params = ImageProcessingParameters()
            return True
        except Exception:
            return False
    
    def get_image_info(self) -> Optional[dict]:
        """Получает информацию о текущем изображении в виде словаря"""
        if not self._current_image:
            return None
        
        info = self._current_image.info
        return {
            "Размер файла": f"{info.file_size_mb:.2f} МБ ({info.file_size} байт)",
            "Разрешение": f"{info.width} x {info.height}",
            "Глубина цвета": f"{info.color_depth} бит",
            "Формат файла": info.format.value,
            "Цветовая модель": info.color_model.value,
            "Модифицировано": "Да" if self._current_image.is_modified else "Нет",
            **info.additional_info,
            **{f"EXIF: {k}": str(v) for k, v in info.exif_data.items()}
        }
