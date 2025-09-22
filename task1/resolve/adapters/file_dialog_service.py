"""
Сервис для работы с файловыми диалогами.
"""
from typing import Optional, Tuple
import FreeSimpleGUI as sg

from domain.interfaces import IFileDialogService


class FreeSimpleGUIFileDialogService(IFileDialogService):
    """Сервис файловых диалогов на основе FreeSimpleGUI"""
    
    def open_file_dialog(self, file_types: Tuple[Tuple[str, str], ...]) -> Optional[str]:
        """Открывает диалог выбора файла"""
        try:
            filename = sg.popup_get_file(
                'Выберите изображение',
                file_types=file_types,
                no_window=True
            )
            return filename if filename else None
            
        except Exception as e:
            print(f"Ошибка открытия диалога выбора файла: {e}")
            return None
    
    def save_file_dialog(self, file_types: Tuple[Tuple[str, str], ...], default_extension: str = "") -> Optional[str]:
        """Открывает диалог сохранения файла"""
        try:
            filename = sg.popup_get_file(
                'Сохранить изображение как',
                save_as=True,
                file_types=file_types,
                default_extension=default_extension,
                no_window=True
            )
            return filename if filename else None
            
        except Exception as e:
            print(f"Ошибка открытия диалога сохранения файла: {e}")
            return None
