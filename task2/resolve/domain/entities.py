from abc import ABC, abstractmethod
from typing import Optional, List
import numpy as np


class Image:
    def __init__(self, data: np.ndarray):
        self.data = data
    
    @property
    def shape(self):
        return self.data.shape
    
    @property
    def width(self):
        return self.data.shape[1] if len(self.data.shape) > 1 else 0
    
    @property
    def height(self):
        return self.data.shape[0] if len(self.data.shape) > 0 else 0


class StructuralElement:
    def __init__(self, kernel: np.ndarray, anchor: Optional[tuple] = None):
        self.kernel = kernel
        self.anchor = anchor if anchor else (kernel.shape[0] // 2, kernel.shape[1] // 2)


class MorphologicalOperation(ABC):
    @abstractmethod
    def apply(self, image: Image, structural_element: StructuralElement) -> Image:
        pass


class ImageFilter(ABC):
    @abstractmethod
    def apply(self, image: Image) -> Image:
        pass


class CustomFilter:
    def __init__(self, kernel: np.ndarray):
        self.kernel = kernel
