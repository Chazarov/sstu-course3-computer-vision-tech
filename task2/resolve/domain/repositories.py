from abc import ABC, abstractmethod
from domain.entities import Image


class ImageRepository(ABC):
    @abstractmethod
    def load(self, path: str) -> Image:
        pass
    
    @abstractmethod
    def save(self, image: Image, path: str) -> None:
        pass

