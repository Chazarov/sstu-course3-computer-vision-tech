"""
Адаптер для работы с изображениями через Pillow.
"""
import os
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image as PILImage, ImageEnhance
from PIL.ExifTags import TAGS

from domain.models import Image, ImageInfo, ColorModel, ImageFormat
from domain.interfaces import IImageRepository, IExifReader


class PillowImageRepository(IImageRepository):
    """Репозиторий для работы с изображениями через Pillow"""
    
    def __init__(self, exif_reader: IExifReader):
        self._exif_reader = exif_reader
    
    def load_image(self, file_path: str) -> Optional[Image]:
        """Загружает изображение из файла"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Загружаем изображение
            pil_image = PILImage.open(file_path)
            
            # Конвертируем в RGB если необходимо (для единообразия)
            if pil_image.mode not in ['RGB', 'RGBA', 'L']:
                pil_image = pil_image.convert('RGB')
            
            # Преобразуем в numpy array
            image_data = np.array(pil_image)
            
            # Получаем информацию об изображении
            info = self.get_image_info(file_path)
            if not info:
                return None
            
            return Image(file_path, image_data, info)
            
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            return None
    
    def save_image(self, image: Image, file_path: str) -> bool:
        """Сохраняет изображение в файл"""
        try:
            # Преобразуем numpy array в PIL Image
            image_data = image.current_data
            
            # Обрабатываем разные форматы данных
            if len(image_data.shape) == 2:  # Grayscale
                pil_image = PILImage.fromarray(image_data, mode='L')
            elif len(image_data.shape) == 3:
                if image_data.shape[2] == 3:  # RGB
                    pil_image = PILImage.fromarray(image_data, mode='RGB')
                elif image_data.shape[2] == 4:  # RGBA
                    pil_image = PILImage.fromarray(image_data, mode='RGBA')
                else:
                    return False
            else:
                return False
            
            # Определяем формат по расширению файла
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            format_map = {
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG',
                '.png': 'PNG',
                '.bmp': 'BMP',
                '.tiff': 'TIFF',
                '.tif': 'TIFF',
                '.gif': 'GIF',
                '.webp': 'WEBP'
            }
            
            format_name = format_map.get(ext, 'PNG')
            
            # Сохраняем
            pil_image.save(file_path, format=format_name)
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения изображения: {e}")
            return False
    
    def get_image_info(self, file_path: str) -> Optional[ImageInfo]:
        """Получает информацию об изображении"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Получаем размер файла
            file_size = os.path.getsize(file_path)
            
            # Открываем изображение для получения метаданных
            with PILImage.open(file_path) as pil_image:
                width, height = pil_image.size
                
                # Определяем глубину цвета
                mode_to_depth = {
                    '1': 1,      # 1-bit pixels, black and white
                    'L': 8,      # 8-bit pixels, black and white
                    'P': 8,      # 8-bit pixels, mapped to any other mode using a color palette
                    'RGB': 24,   # 3x8-bit pixels, true color
                    'RGBA': 32,  # 4x8-bit pixels, true color with transparency mask
                    'CMYK': 32,  # 4x8-bit pixels, color separation
                    'YCbCr': 24, # 3x8-bit pixels, color video format
                    'LAB': 24,   # 3x8-bit pixels, the L*a*b* color space
                    'HSV': 24,   # 3x8-bit pixels, Hue, Saturation, Value color space
                }
                
                color_depth = mode_to_depth.get(pil_image.mode, 24)
                
                # Определяем формат
                format_name = pil_image.format or "UNKNOWN"
                try:
                    image_format = ImageFormat(format_name)
                except ValueError:
                    image_format = ImageFormat.OTHER
                
                # Определяем цветовую модель
                try:
                    color_model = ColorModel(pil_image.mode)
                except ValueError:
                    color_model = ColorModel.RGB
            
            # Получаем EXIF данные
            exif_data = self._exif_reader.read_exif(file_path)
            
            # Дополнительная информация
            additional_info = {
                "Путь к файлу": file_path,
                "Имя файла": os.path.basename(file_path)
            }
            
            return ImageInfo(
                file_size=file_size,
                width=width,
                height=height,
                color_depth=color_depth,
                format=image_format,
                color_model=color_model,
                exif_data=exif_data,
                additional_info=additional_info
            )
            
        except Exception as e:
            print(f"Ошибка получения информации об изображении: {e}")
            return None


class ExifReader(IExifReader):
    """Читатель EXIF данных"""
    
    def read_exif(self, file_path: str) -> Dict[str, Any]:
        """Читает EXIF данные из файла"""
        try:
            with PILImage.open(file_path) as image:
                exif_dict = {}
                
                # Получаем EXIF данные через Pillow
                exif_data = image._getexif()
                
                if exif_data is not None:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        # Преобразуем значение в строку для отображения
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8')
                            except UnicodeDecodeError:
                                value = str(value)
                        elif isinstance(value, tuple) and len(value) == 2:
                            # Обрабатываем дроби (например, для выдержки)
                            try:
                                value = f"{value[0]}/{value[1]}"
                            except:
                                value = str(value)
                        
                        exif_dict[str(tag)] = str(value)
                
                # Добавляем базовую информацию, если EXIF данных мало
                if len(exif_dict) < 5:
                    exif_dict.update({
                        "Режим изображения": image.mode,
                        "Размер": f"{image.size[0]}x{image.size[1]}",
                        "Формат": image.format or "Неизвестно",
                        "Имеет анимацию": str(getattr(image, 'is_animated', False)),
                        "Количество кадров": str(getattr(image, 'n_frames', 1))
                    })
                
                return exif_dict
                
        except Exception as e:
            print(f"Ошибка чтения EXIF: {e}")
            return {
                "Ошибка": "Не удалось прочитать EXIF данные",
                "Причина": str(e),
                "Формат файла": os.path.splitext(file_path)[1].upper(),
                "Размер файла": f"{os.path.getsize(file_path)} байт",
                "Статус": "EXIF недоступен"
            }
