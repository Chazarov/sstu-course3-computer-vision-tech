import cv2
import numpy as np
from domain.entities import Image
from domain.repositories import ImageRepository


class OpenCVImageRepository(ImageRepository):
    def load(self, path: str) -> Image:
        data = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if data is None:
            raise ValueError(f"Не удалось загрузить изображение: {path}")
        return Image(data)
    
    def save(self, image: Image, path: str) -> None:
        cv2.imwrite(path, image.data)

