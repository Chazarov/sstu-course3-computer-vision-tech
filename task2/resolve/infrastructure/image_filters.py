import cv2
import numpy as np
from domain.entities import Image, ImageFilter, CustomFilter


class SharpeningFilter(ImageFilter):
    def apply(self, image: Image) -> Image:
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]], dtype=np.float32)
        result = cv2.filter2D(image.data, -1, kernel)
        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image(result)


class MotionBlurFilter(ImageFilter):
    def __init__(self, size: int, angle: float):
        self.size = size
        self.angle = angle
    
    def apply(self, image: Image) -> Image:
        kernel = np.zeros((self.size, self.size), dtype=np.float32)
        angle_rad = np.deg2rad(self.angle)
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        center = self.size // 2
        
        for i in range(self.size):
            x = int(center + (i - center) * cos_angle)
            y = int(center + (i - center) * sin_angle)
            if 0 <= x < self.size and 0 <= y < self.size:
                kernel[y, x] = 1.0
        
        kernel /= np.sum(kernel)
        result = cv2.filter2D(image.data, -1, kernel)
        return Image(result)


class EmbossFilter(ImageFilter):
    def apply(self, image: Image) -> Image:
        kernel = np.array([[-2, -1, 0],
                          [-1,  1, 1],
                          [ 0,  1, 2]], dtype=np.float32)
        result = cv2.filter2D(image.data, -1, kernel)
        result = cv2.addWeighted(image.data, 0.5, result, 0.5, 128)
        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image(result)


class MedianFilter(ImageFilter):
    def __init__(self, size: int):
        self.size = size
    
    def apply(self, image: Image) -> Image:
        result = cv2.medianBlur(image.data, self.size)
        return Image(result)


class CustomFilterImplementation(ImageFilter):
    def __init__(self, custom_filter: CustomFilter):
        self._custom_filter = custom_filter
    
    def apply(self, image: Image) -> Image:
        kernel = self._custom_filter.kernel.astype(np.float32)
        if np.sum(kernel) != 0:
            kernel = kernel / np.sum(kernel)
        result = cv2.filter2D(image.data, -1, kernel)
        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image(result)

