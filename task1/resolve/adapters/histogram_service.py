"""
Сервис для работы с гистограммами.
"""
import io
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image as PILImage

from domain.models import Histogram
from domain.interfaces import IHistogramService, IImageDisplayService

# Используем Agg backend для matplotlib (без GUI)
matplotlib.use('Agg')


class MatplotlibHistogramService(IHistogramService):
    """Сервис гистограмм на основе Matplotlib"""
    
    def calculate_histogram(self, image_data: np.ndarray) -> Histogram:
        """Вычисляет гистограмму изображения"""
        try:
            if len(image_data.shape) == 2:
                # Grayscale image
                hist, _ = np.histogram(image_data.flatten(), bins=256, range=(0, 256))
                return Histogram(grayscale=hist)
            
            elif len(image_data.shape) == 3:
                # Color image
                if image_data.shape[2] >= 3:
                    # RGB channels
                    hist_r, _ = np.histogram(image_data[:,:,0].flatten(), bins=256, range=(0, 256))
                    hist_g, _ = np.histogram(image_data[:,:,1].flatten(), bins=256, range=(0, 256))
                    hist_b, _ = np.histogram(image_data[:,:,2].flatten(), bins=256, range=(0, 256))
                    
                    return Histogram(
                        red_channel=hist_r,
                        green_channel=hist_g,
                        blue_channel=hist_b
                    )
            
            raise ValueError("Неподдерживаемый формат изображения для гистограммы")
            
        except Exception as e:
            print(f"Ошибка вычисления гистограммы: {e}")
            raise
    
    def plot_histogram(self, histogram: Histogram, title: str = "", width: float = 10, height: float = 6) -> bytes:
        """Строит график гистограммы и возвращает его как байты"""
        try:
            plt.figure(figsize=(width, height))
            
            if histogram.grayscale is not None:
                plt.plot(range(256), histogram.grayscale, color='black', alpha=0.7)
                plt.fill_between(range(256), histogram.grayscale, alpha=0.3, color='gray')
                plt.title(f'Гистограмма (Градации серого) {title}')
                plt.xlabel('Значение яркости')
                plt.ylabel('Количество пикселей')
                
            elif histogram.has_color_channels():
                plt.plot(range(256), histogram.red_channel, color='red', alpha=0.7, label='Красный')
                plt.plot(range(256), histogram.green_channel, color='green', alpha=0.7, label='Зеленый')
                plt.plot(range(256), histogram.blue_channel, color='blue', alpha=0.7, label='Синий')
                plt.fill_between(range(256), histogram.red_channel, alpha=0.3, color='red')
                plt.fill_between(range(256), histogram.green_channel, alpha=0.3, color='green')
                plt.fill_between(range(256), histogram.blue_channel, alpha=0.3, color='blue')
                plt.title(f'Гистограмма RGB {title}')
                plt.xlabel('Значение яркости')
                plt.ylabel('Количество пикселей')
                plt.legend()
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_bytes = buffer.getvalue()
            buffer.close()
            plt.close()
            
            return image_bytes
            
        except Exception as e:
            print(f"Ошибка построения гистограммы: {e}")
            raise


class PillowDisplayService(IImageDisplayService):
    """Сервис отображения изображений на основе Pillow"""
    
    def prepare_for_display(self, image_data: np.ndarray, max_size: Tuple[int, int] = (800, 600)) -> bytes:
        """Подготавливает изображение для отображения в GUI"""
        try:
            # Преобразуем в PIL Image
            if len(image_data.shape) == 2:
                # Grayscale
                pil_image = PILImage.fromarray(image_data, mode='L')
            elif len(image_data.shape) == 3:
                if image_data.shape[2] == 3:
                    # RGB
                    pil_image = PILImage.fromarray(image_data, mode='RGB')
                elif image_data.shape[2] == 4:
                    # RGBA
                    pil_image = PILImage.fromarray(image_data, mode='RGBA')
                else:
                    raise ValueError("Неподдерживаемое количество каналов")
            else:
                raise ValueError("Неподдерживаемый формат изображения")
            
            # Изменяем размер, сохраняя пропорции
            original_size = pil_image.size
            if original_size[0] > max_size[0] or original_size[1] > max_size[1]:
                pil_image.thumbnail(max_size, PILImage.Resampling.LANCZOS)
            
            # Конвертируем в байты
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            buffer.seek(0)
            image_bytes = buffer.getvalue()
            buffer.close()
            
            return image_bytes
            
        except Exception as e:
            print(f"Ошибка подготовки изображения для отображения: {e}")
            raise
