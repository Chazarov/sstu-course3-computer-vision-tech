import cv2
import numpy as np
from domain.entities import Image, StructuralElement, MorphologicalOperation


class OpenCVErosionOperation(MorphologicalOperation):
    def apply(self, image: Image, structural_element: StructuralElement) -> Image:
        kernel = structural_element.kernel.astype(np.uint8)
        result = cv2.erode(image.data, kernel, anchor=structural_element.anchor, iterations=1)
        return Image(result)


class OpenCVDilationOperation(MorphologicalOperation):
    def apply(self, image: Image, structural_element: StructuralElement) -> Image:
        kernel = structural_element.kernel.astype(np.uint8)
        result = cv2.dilate(image.data, kernel, anchor=structural_element.anchor, iterations=1)
        return Image(result)


class OpenCVOpeningOperation(MorphologicalOperation):
    def apply(self, image: Image, structural_element: StructuralElement) -> Image:
        kernel = structural_element.kernel.astype(np.uint8)
        result = cv2.morphologyEx(image.data, cv2.MORPH_OPEN, kernel, anchor=structural_element.anchor)
        return Image(result)


class OpenCVClosingOperation(MorphologicalOperation):
    def apply(self, image: Image, structural_element: StructuralElement) -> Image:
        kernel = structural_element.kernel.astype(np.uint8)
        result = cv2.morphologyEx(image.data, cv2.MORPH_CLOSE, kernel, anchor=structural_element.anchor)
        return Image(result)


class OpenCVGradientOperation(MorphologicalOperation):
    def apply(self, image: Image, structural_element: StructuralElement) -> Image:
        kernel = structural_element.kernel.astype(np.uint8)
        result = cv2.morphologyEx(image.data, cv2.MORPH_GRADIENT, kernel, anchor=structural_element.anchor)
        return Image(result)


class OpenCVTopHatOperation(MorphologicalOperation):
    def apply(self, image: Image, structural_element: StructuralElement) -> Image:
        kernel = structural_element.kernel.astype(np.uint8)
        result = cv2.morphologyEx(image.data, cv2.MORPH_TOPHAT, kernel, anchor=structural_element.anchor)
        return Image(result)


class OpenCVBlackHatOperation(MorphologicalOperation):
    def apply(self, image: Image, structural_element: StructuralElement) -> Image:
        kernel = structural_element.kernel.astype(np.uint8)
        result = cv2.morphologyEx(image.data, cv2.MORPH_BLACKHAT, kernel, anchor=structural_element.anchor)
        return Image(result)
