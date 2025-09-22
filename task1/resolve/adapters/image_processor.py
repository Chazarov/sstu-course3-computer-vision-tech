"""
Адаптер для обработки изображений.
"""
import numpy as np
from PIL import Image as PILImage, ImageEnhance
import cv2

from domain.interfaces import IImageProcessor


class PillowImageProcessor(IImageProcessor):
    """Процессор изображений на основе Pillow и OpenCV"""
    
    def convert_to_grayscale(self, image_data: np.ndarray) -> np.ndarray:
        """Преобразует изображение в градации серого"""
        try:
            if len(image_data.shape) == 2:
                # Уже в градациях серого
                return image_data
            
            if len(image_data.shape) == 3:
                if image_data.shape[2] == 3:  # RGB
                    # Используем стандартные веса для RGB -> Grayscale
                    grayscale = np.dot(image_data[...,:3], [0.2989, 0.5870, 0.1140])
                    return grayscale.astype(np.uint8)
                elif image_data.shape[2] == 4:  # RGBA
                    # Игнорируем альфа-канал
                    rgb = image_data[:,:,:3]
                    grayscale = np.dot(rgb, [0.2989, 0.5870, 0.1140])
                    return grayscale.astype(np.uint8)
            
            raise ValueError("Неподдерживаемый формат изображения")
            
        except Exception as e:
            print(f"Ошибка преобразования в градации серого: {e}")
            raise
    
    def adjust_brightness(self, image_data: np.ndarray, brightness: float) -> np.ndarray:
        """Изменяет яркость изображения"""
        try:
            # brightness от -100 до 100
            # Преобразуем в множитель от 0.0 до 2.0
            factor = 1.0 + (brightness / 100.0)
            
            if len(image_data.shape) == 2:
                # Grayscale
                adjusted = image_data.astype(np.float32) * factor
                adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
                return adjusted
            else:
                # Color image
                pil_image = PILImage.fromarray(image_data)
                enhancer = ImageEnhance.Brightness(pil_image)
                enhanced = enhancer.enhance(factor)
                return np.array(enhanced)
                
        except Exception as e:
            print(f"Ошибка изменения яркости: {e}")
            raise
    
    def adjust_contrast(self, image_data: np.ndarray, contrast: float) -> np.ndarray:
        """Изменяет контрастность изображения"""
        try:
            if len(image_data.shape) == 2:
                # Grayscale - используем формулу контрастности
                mean = np.mean(image_data)
                adjusted = (image_data - mean) * contrast + mean
                adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
                return adjusted
            else:
                # Color image
                pil_image = PILImage.fromarray(image_data)
                enhancer = ImageEnhance.Contrast(pil_image)
                enhanced = enhancer.enhance(contrast)
                return np.array(enhanced)
                
        except Exception as e:
            print(f"Ошибка изменения контрастности: {e}")
            raise
    
    def adjust_saturation(self, image_data: np.ndarray, saturation: float) -> np.ndarray:
        """Изменяет насыщенность изображения"""
        try:
            if len(image_data.shape) == 2:
                # Для grayscale насыщенность не применяется
                return image_data
            
            pil_image = PILImage.fromarray(image_data)
            enhancer = ImageEnhance.Color(pil_image)
            enhanced = enhancer.enhance(saturation)
            return np.array(enhanced)
            
        except Exception as e:
            print(f"Ошибка изменения насыщенности: {e}")
            raise
    
    def rotate_image(self, image_data: np.ndarray, angle: int) -> np.ndarray:
        """Поворачивает изображение на заданный угол"""
        try:
            if angle == 0:
                return image_data
            
            # Поворот на 90, 180, 270 градусов
            if angle == 90:
                return np.rot90(image_data, k=1)
            elif angle == 180:
                return np.rot90(image_data, k=2)
            elif angle == 270:
                return np.rot90(image_data, k=3)
            else:
                raise ValueError(f"Неподдерживаемый угол поворота: {angle}")
                
        except Exception as e:
            print(f"Ошибка поворота изображения: {e}")
            raise
    
    def apply_linear_correction(self, image_data: np.ndarray, min_val: int, max_val: int) -> np.ndarray:
        """Применяет линейную коррекцию к черно-белому изображению"""
        try:
            if len(image_data.shape) != 2:
                raise ValueError("Линейная коррекция применяется только к черно-белым изображениям")
            
            # Находим текущие минимальные и максимальные значения
            current_min = np.min(image_data)
            current_max = np.max(image_data)
            
            if current_max == current_min:
                return image_data
            
            # Применяем линейное преобразование
            # new_value = (old_value - current_min) * (max_val - min_val) / (current_max - current_min) + min_val
            corrected = ((image_data.astype(np.float32) - current_min) * 
                        (max_val - min_val) / (current_max - current_min) + min_val)
            
            corrected = np.clip(corrected, 0, 255).astype(np.uint8)
            return corrected
            
        except Exception as e:
            print(f"Ошибка линейной коррекции: {e}")
            raise
    
    def apply_nonlinear_correction(self, image_data: np.ndarray, gamma: float) -> np.ndarray:
        """Применяет нелинейную (гамма) коррекцию к черно-белому изображению"""
        try:
            if len(image_data.shape) != 2:
                raise ValueError("Нелинейная коррекция применяется только к черно-белым изображениям")
            
            # Нормализуем к диапазону [0, 1]
            normalized = image_data.astype(np.float32) / 255.0
            
            # Применяем гамма-коррекцию
            corrected = np.power(normalized, gamma)
            
            # Возвращаем к диапазону [0, 255]
            corrected = (corrected * 255).astype(np.uint8)
            
            return corrected
            
        except Exception as e:
            print(f"Ошибка нелинейной коррекции: {e}")
            raise
