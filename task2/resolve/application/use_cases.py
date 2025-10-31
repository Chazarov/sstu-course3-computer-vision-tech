from domain.entities import Image, StructuralElement, MorphologicalOperation
from domain.repositories import ImageRepository


class LoadImageUseCase:
    def __init__(self, repository: ImageRepository):
        self._repository = repository
    
    def execute(self, path: str) -> Image:
        return self._repository.load(path)


class SaveImageUseCase:
    def __init__(self, repository: ImageRepository):
        self._repository = repository
    
    def execute(self, image: Image, path: str) -> None:
        self._repository.save(image, path)


class ApplyMorphologicalOperationUseCase:
    def __init__(self, operation: MorphologicalOperation):
        self._operation = operation
    
    def execute(self, image: Image, structural_element: StructuralElement) -> Image:
        return self._operation.apply(image, structural_element)

