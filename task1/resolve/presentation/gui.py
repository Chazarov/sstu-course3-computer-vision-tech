from typing import Optional, Dict, Any
import FreeSimpleGUI as sg
import io

from services.image_service import ImageService
from domain.models import ImageProcessingParameters
from domain.interfaces import IFileDialogService


class ImageProcessorGUI:
    """Главное окно приложения для обработки изображений"""
    
    def __init__(self, image_service: ImageService, file_dialog_service: IFileDialogService):
        self._image_service = image_service
        self._file_dialog_service = file_dialog_service
        self._window: Optional[sg.Window] = None
        self._current_histogram_window: Optional[sg.Window] = None
        
        self._processing_params = ImageProcessingParameters()
        
        sg.theme('LightBlue3')
        
        self._image_file_types = (
            ("Все изображения", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif *.webp"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff *.tif"),
            ("GIF", "*.gif"),
            ("WEBP", "*.webp"),
            ("Все файлы", "*.*")
        )
    
    def create_layout(self) -> list:
        """Создает макет интерфейса"""
        
        # Колонка с изображением
        image_column = [
            [sg.Text('Изображение:', font=('Arial', 12, 'bold'))],
            [sg.Image(key='-IMAGE-', size=(800, 600))],
            [sg.HorizontalSeparator()],
            [
                sg.Button('Загрузить изображение', key='-LOAD-', size=(20, 1)),
                sg.Button('Сохранить изображение', key='-SAVE-', size=(20, 1), disabled=True),
                sg.Button('Сбросить к оригиналу', key='-RESET-', size=(20, 1), disabled=True)
            ]
        ]
        
        # Колонка с информацией об изображении
        info_column = [
            [sg.Text('Информация об изображении:', font=('Arial', 12, 'bold'))],
            [sg.Frame('Основные параметры', [
                [sg.Text('Размер файла:', size=(15, 1)), sg.Text('', key='-FILE_SIZE-', size=(25, 1))],
                [sg.Text('Разрешение:', size=(15, 1)), sg.Text('', key='-RESOLUTION-', size=(25, 1))],
                [sg.Text('Глубина цвета:', size=(15, 1)), sg.Text('', key='-COLOR_DEPTH-', size=(25, 1))],
                [sg.Text('Формат файла:', size=(15, 1)), sg.Text('', key='-FORMAT-', size=(25, 1))],
                [sg.Text('Цветовая модель:', size=(15, 1)), sg.Text('', key='-COLOR_MODEL-', size=(25, 1))],
                [sg.Text('Модифицировано:', size=(15, 1)), sg.Text('', key='-MODIFIED-', size=(25, 1))],
            ], font=('Arial', 10), pad=(5, 5))],
            [sg.Frame('Дополнительная информация', [
                [sg.Text('Путь к файлу:', size=(15, 1)), sg.Text('', key='-FILE_PATH-', size=(25, 1)), sg.Button('Копировать', key='-COPY_PATH-', size=(8, 1))],
                [sg.Text('Имя файла:', size=(15, 1)), sg.Text('', key='-FILE_NAME-', size=(25, 1)), sg.Button('Копировать', key='-COPY_NAME-', size=(8, 1))],
            ], font=('Arial', 10), pad=(5, 5))],
            [sg.Frame('EXIF данные', [
                [sg.Multiline('', key='-EXIF_INFO-', size=(40, 6), disabled=True, font=('Courier', 9), background_color='#f0f0f0')]
            ], font=('Arial', 10), pad=(5, 5))],
            [sg.HorizontalSeparator()],
            [sg.Text('Гистограмма:', font=('Arial', 11, 'bold'))],
            [
                sg.Button('Показать текущую', key='-HIST_CURRENT-', size=(18, 1), disabled=True),
                sg.Button('Показать оригинальную', key='-HIST_ORIGINAL-', size=(18, 1), disabled=True)
            ],
            [
                sg.Button('Сравнить гистограммы', key='-HIST_COMPARE-', size=(37, 1), disabled=True)
            ]
        ]

        processing_column = [
            [sg.Text('Параметры обработки:', font=('Arial', 12, 'bold'))],
            [
                sg.Text('Яркость:', size=(12, 1)),
                sg.Slider(range=(-100, 100), default_value=0, orientation='h', size=(15, 15), key='-BRIGHTNESS-'),
                sg.Button('Применить', key='-BRIGHTNESS_APPLY-', size=(8, 1), disabled=True)
            ],
            [
                sg.Text('Контрастность:', size=(12, 1)),
                sg.Slider(range=(0.1, 3.0), default_value=1.0, resolution=0.1, orientation='h',
                         size=(15, 15), key='-CONTRAST-'),
                sg.Button('Применить', key='-CONTRAST_APPLY-', size=(8, 1), disabled=True)
            ],
            [
                sg.Text('Насыщенность:', size=(12, 1)),
                sg.Slider(range=(0.0, 3.0), default_value=1.0, resolution=0.1, orientation='h',
                         size=(15, 15), key='-SATURATION-'),
                sg.Button('Применить', key='-SATURATION_APPLY-', size=(8, 1), disabled=True)
            ],
            [sg.HorizontalSeparator()],
            [sg.Text('Преобразования:', font=('Arial', 11, 'bold'))],
            [
                sg.Button('В градации серого', key='-GRAYSCALE-', size=(18, 1), disabled=True),
                sg.Button('Повернуть на 90°', key='-ROTATE-', size=(18, 1), disabled=True)
            ],
            [sg.HorizontalSeparator()],
            [sg.Text('Коррекция изображения:', font=('Arial', 11, 'bold'))],
            [
                sg.Text('Линейная:', size=(8, 1)),
                sg.Slider(range=(0.1, 2.0), default_value=1.0, resolution=0.1, orientation='h', size=(15, 15), key='-LINEAR_FACTOR-', enable_events=True),
                sg.Button('Применить', key='-LINEAR_CORRECT-', size=(8, 1), disabled=True)
            ],
            [
                sg.Text('Логарифмическая:', size=(12, 1)),
                sg.Slider(range=(0.1, 2.0), default_value=1.0, resolution=0.1, orientation='h', size=(11, 15), key='-LOG_FACTOR-', enable_events=True),
                sg.Button('Применить', key='-LOG_CORRECT-', size=(8, 1), disabled=True)
            ],
            [
                sg.Text('Гамма:', size=(8, 1)),
                sg.Slider(range=(0.1, 3.0), default_value=1.0, resolution=0.1, orientation='h', size=(15, 15), key='-GAMMA_FACTOR-', enable_events=True),
                sg.Button('Применить', key='-GAMMA_CORRECT-', size=(8, 1), disabled=True)
            ]
        ]
        right_column_scrollable = [
            [sg.Column(info_column, vertical_alignment='top')],
            [sg.HorizontalSeparator()],
            [sg.Column(processing_column, vertical_alignment='top')]
        ]
        layout = [
            [
                sg.Column(image_column, vertical_alignment='top'),
                sg.VerticalSeparator(),
                sg.Column(
                    right_column_scrollable, 
                    vertical_alignment='top',
                    scrollable=True,
                    vertical_scroll_only=True,
                    size=(450, 700),
                    pad=(5, 5)
                )
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Text('Статус: Готов к работе', key='-STATUS-'),
                sg.Push(),
                sg.Button('Выход', key='-EXIT-')
            ]
        ]
        
        return layout
    
    def create_window(self) -> sg.Window:
        """Создает главное окно"""
        layout = self.create_layout()
        
        window = sg.Window(
            'Обработка изображений',
            layout,
            finalize=True,
            resizable=True,
            location=(50, 50),
            size=(1400, 800)
        )
        
        return window
    
    def update_status(self, message: str) -> None:
        """Обновляет статусную строку"""
        if self._window:
            self._window['-STATUS-'].update(f'Статус: {message}')
    
    def update_image_display(self) -> None:
        """Обновляет отображение изображения"""
        try:
            if not self._image_service.current_image:
                return
            
            image_bytes = self._image_service.prepare_image_for_display()
            if image_bytes and self._window:
                self._window['-IMAGE-'].update(data=image_bytes)
                
        except Exception as e:
            self.update_status(f'Ошибка отображения: {str(e)}')
    
    def update_image_info(self) -> None:
        """Обновляет информацию об изображении"""
        try:
            info = self._image_service.get_image_info()
            if info and self._window:
                self._window['-FILE_SIZE-'].update(info.get('Размер файла', ''))
                self._window['-RESOLUTION-'].update(info.get('Разрешение', ''))
                self._window['-COLOR_DEPTH-'].update(info.get('Глубина цвета', ''))
                self._window['-FORMAT-'].update(info.get('Формат файла', ''))
                self._window['-COLOR_MODEL-'].update(info.get('Цветовая модель', ''))
                self._window['-MODIFIED-'].update(info.get('Модифицировано', ''))
                
                file_path = info.get('Путь к файлу', '')
                if len(file_path) > 40:
                    file_path = '...' + file_path[-37:]
                self._window['-FILE_PATH-'].update(file_path)
                self._window['-FILE_NAME-'].update(info.get('Имя файла', ''))
                
                exif_lines = []
                for key, value in info.items():
                    if key.startswith('EXIF:'):
                        exif_key = key.replace('EXIF: ', '')
                        if len(str(value)) > 50:
                            value = str(value)[:47] + '...'
                        exif_lines.append(f'{exif_key:<20}: {value}')
                
                if exif_lines:
                    exif_text = '\n'.join(exif_lines)
                else:
                    exif_text = 'EXIF данные отсутствуют или недоступны'
                
                self._window['-EXIF_INFO-'].update(exif_text)
                
        except Exception as e:
            self.update_status(f'Ошибка получения информации: {str(e)}')
    
    def clear_image_info(self) -> None:
        """Очищает информацию об изображении"""
        if not self._window:
            return
        
        self._window['-FILE_SIZE-'].update('')
        self._window['-RESOLUTION-'].update('')
        self._window['-COLOR_DEPTH-'].update('')
        self._window['-FORMAT-'].update('')
        self._window['-COLOR_MODEL-'].update('')
        self._window['-MODIFIED-'].update('')
        
        self._window['-FILE_PATH-'].update('')
        self._window['-FILE_NAME-'].update('')
        
        self._window['-EXIF_INFO-'].update('')
    
    def copy_to_clipboard(self, text: str) -> None:
        """Копирует текст в буфер обмена"""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Скрываем главное окно
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()  # Обновляем буфер обмена
            root.destroy()
            self.update_status('Текст скопирован в буфер обмена')
        except Exception as e:
            self.update_status(f'Ошибка копирования: {str(e)}')
    
    def copy_file_path(self) -> None:
        """Копирует путь к файлу в буфер обмена"""
        if not self._window:
            return
        
        file_path = self._window['-FILE_PATH-'].get()
        if file_path:
            # Получаем полный путь из информации об изображении
            info = self._image_service.get_image_info()
            full_path = info.get('Путь к файлу', '')
            if full_path:
                self.copy_to_clipboard(full_path)
            else:
                self.copy_to_clipboard(file_path)
        else:
            self.update_status('Нет пути к файлу для копирования')
    
    def copy_file_name(self) -> None:
        """Копирует имя файла в буфер обмена"""
        if not self._window:
            return
        
        file_name = self._window['-FILE_NAME-'].get()
        if file_name:
            self.copy_to_clipboard(file_name)
        else:
            self.update_status('Нет имени файла для копирования')
    
    def enable_image_controls(self, enabled: bool) -> None:
        """Включает/выключает элементы управления изображением"""
        if not self._window:
            return
        
        controls = [
            '-SAVE-', '-RESET-', '-GRAYSCALE-', '-ROTATE-',
            '-HIST_CURRENT-', '-HIST_ORIGINAL-', '-HIST_COMPARE-',
            '-BRIGHTNESS_APPLY-', '-CONTRAST_APPLY-', '-SATURATION_APPLY-',
            '-LINEAR_CORRECT-', '-LOG_CORRECT-', '-GAMMA_CORRECT-'
        ]
        
        for control in controls:
            self._window[control].update(disabled=not enabled)
    
    def load_image(self) -> None:
        """Загружает изображение"""
        try:
            filename = self._file_dialog_service.open_file_dialog(self._image_file_types)
            if not filename:
                return
            
            self.update_status('Загрузка изображения...')
            
            if self._image_service.load_image(filename):
                self.update_status('Изображение загружено успешно')
                self.update_image_display()
                self.update_image_info()
                self.enable_image_controls(True)
                self.reset_processing_params()
            else:
                self.update_status('Ошибка загрузки изображения')
                self.clear_image_info()
                self.enable_image_controls(False)
                
        except Exception as e:
            self.update_status(f'Ошибка: {str(e)}')
    
    def save_image(self) -> None:
        """Сохраняет изображение"""
        try:
            filename = self._file_dialog_service.save_file_dialog(
                self._image_file_types, ".png"
            )
            if not filename:
                return
            
            self.update_status('Сохранение изображения...')
            
            if self._image_service.save_image(filename):
                self.update_status('Изображение сохранено успешно')
            else:
                self.update_status('Ошибка сохранения изображения')
                
        except Exception as e:
            self.update_status(f'Ошибка: {str(e)}')
    
    def reset_processing_params(self) -> None:
        """Сбрасывает параметры обработки"""
        if not self._window:
            return
        
        # Сбрасываем параметры в сервисе
        self._image_service.reset_processing_params()
        
        # Обновляем UI элементы
        self._window['-BRIGHTNESS-'].update(0)
        self._window['-CONTRAST-'].update(1.0)
        self._window['-SATURATION-'].update(1.0)
        self._window['-LINEAR_FACTOR-'].update(1.0)
        self._window['-LOG_FACTOR-'].update(1.0)
        self._window['-GAMMA_FACTOR-'].update(1.0)
        self._processing_params = ImageProcessingParameters()
        
        # Обновляем отображение изображения
        self.update_image_display()
    
    def apply_processing_params(self) -> None:
        """Применяет текущие параметры обработки"""
        try:
            if self._image_service.apply_processing_parameters(self._processing_params):
                self.update_image_display()
                self.update_status('Параметры применены')
            else:
                self.update_status('Ошибка применения параметров')
                
        except Exception as e:
            self.update_status(f'Ошибка: {str(e)}')
    
    def show_histogram(self, histogram_type: str) -> None:
        """Показывает гистограмму"""
        try:
            if histogram_type == 'current':
                histogram = self._image_service.get_histogram()
                title = '(Текущее)'
            elif histogram_type == 'original':
                histogram = self._image_service.get_original_histogram()
                title = '(Оригинальное)'
            elif histogram_type == 'compare':
                self.show_histogram_comparison()
                return
            else:
                return
            
            if not histogram:
                self.update_status('Не удалось получить гистограмму')
                return
            
            histogram_bytes = self._image_service.plot_histogram(histogram, title)
            if histogram_bytes:
                self.create_histogram_window(histogram_bytes, f'Гистограмма {title}')
            else:
                self.update_status('Ошибка построения гистограммы')
                
        except Exception as e:
            self.update_status(f'Ошибка: {str(e)}')
    
    def show_histogram_comparison(self) -> None:
        """Показывает сравнение гистограмм"""
        try:
            current_hist = self._image_service.get_histogram()
            original_hist = self._image_service.get_original_histogram()
            
            if not current_hist or not original_hist:
                self.update_status('Не удалось получить гистограммы для сравнения')
                return
            
            current_bytes = self._image_service.plot_histogram(current_hist, '(Текущее)', 4, 3)
            original_bytes = self._image_service.plot_histogram(original_hist, '(Оригинальное)', 4, 3)
            
            if current_bytes and original_bytes:
                self.create_comparison_window(original_bytes, current_bytes)
            else:
                self.update_status('Ошибка построения гистограмм')
                
        except Exception as e:
            self.update_status(f'Ошибка: {str(e)}')
    
    def create_histogram_window(self, histogram_bytes: bytes, title: str) -> None:
        """Создает окно с гистограммой"""
        layout = [
            [sg.Image(data=histogram_bytes)],
            [sg.Button('Закрыть', key='-CLOSE_HIST-')]
        ]
        
        if self._current_histogram_window:
            self._current_histogram_window.close()
        
        self._current_histogram_window = sg.Window(
            title,
            layout,
            finalize=True,
            modal=False,
            location=(200, 200)
        )
    
    def create_comparison_window(self, original_bytes: bytes, current_bytes: bytes) -> None:
        """Создает окно сравнения гистограмм с горизонтальным расположением"""
        layout = [
            [
                sg.Column([[sg.Text('Оригинальная гистограмма:', font=('Arial', 12, 'bold'))],
                        [sg.Image(data=original_bytes)]], vertical_alignment='top'),
                sg.VerticalSeparator(),
                sg.Column([[sg.Text('Текущая гистограмма:', font=('Arial', 12, 'bold'))],
                        [sg.Image(data=current_bytes)]], vertical_alignment='top')
            ],
            [sg.Button('Закрыть', key='-CLOSE_COMP-')]
        ]

        if self._current_histogram_window:
            self._current_histogram_window.close()

        self._current_histogram_window = sg.Window(
            'Сравнение гистограмм',
            layout,
            finalize=True,
            modal=False,
            location=(200, 200),
            resizable=True
        )
    
    def run(self) -> None:
        """Запускает главный цикл приложения"""
        self._window = self.create_window()
        
        try:
            while True:
                window, event, values = sg.read_all_windows(timeout=100)
                
                if event == sg.WIN_CLOSED or event == '-EXIT-':
                    break
                
                if window == self._window:
                    self.handle_main_window_event(event, values)
                elif window == self._current_histogram_window:
                    if event in [sg.WIN_CLOSED, '-CLOSE_HIST-', '-CLOSE_COMP-']:
                        window.close()
                        self._current_histogram_window = None
        
        finally:
            if self._current_histogram_window:
                self._current_histogram_window.close()
            if self._window:
                self._window.close()
    
    def handle_main_window_event(self, event: str, values: Dict[str, Any]) -> None:
        """Обрабатывает события главного окна"""
        try:
            if event == '-LOAD-':
                self.load_image()
            
            elif event == '-SAVE-':
                self.save_image()
            
            elif event == '-RESET-':
                if self._image_service.reset_to_original():
                    self.update_image_display()
                    self.reset_processing_params()
                    self.update_status('Изображение сброшено к оригиналу')
                    self.enable_image_controls(True)
                else:
                    self.update_status('Ошибка сброса изображения')
            
            elif event == '-GRAYSCALE-':
                if self._image_service.convert_to_grayscale():
                    self.update_image_display()
                    self.update_status('Изображение преобразовано в градации серого')
                    self.enable_image_controls(True)
                else:
                    self.update_status('Ошибка преобразования в градации серого')
            
            elif event == '-ROTATE-':
                self._processing_params.rotation = (self._processing_params.rotation + 90) % 360
                self.apply_processing_params()
            
            elif event == '-BRIGHTNESS_APPLY-':
                self._processing_params.brightness = values['-BRIGHTNESS-']
                self.apply_processing_params()
            
            elif event == '-CONTRAST_APPLY-':
                self._processing_params.contrast = values['-CONTRAST-']
                self.apply_processing_params()
            
            elif event == '-SATURATION_APPLY-':
                self._processing_params.saturation = values['-SATURATION-']
                self.apply_processing_params()
            
            elif event == '-LINEAR_CORRECT-':
                factor = values['-LINEAR_FACTOR-']
                if self._image_service.apply_linear_correction(factor):
                    self.update_image_display()
                    self.update_status('Линейная коррекция применена')
                else:
                    self.update_status('Ошибка линейной коррекции')
            
            elif event == '-LOG_CORRECT-':
                factor = values['-LOG_FACTOR-']
                if self._image_service.apply_logarithmic_correction(factor):
                    self.update_image_display()
                    self.update_status('Логарифмическая коррекция применена')
                else:
                    self.update_status('Ошибка логарифмической коррекции')
            
            elif event == '-GAMMA_CORRECT-':
                gamma = values['-GAMMA_FACTOR-']
                if self._image_service.apply_gamma_correction(gamma):
                    self.update_image_display()
                    self.update_status('Гамма коррекция применена')
                else:
                    self.update_status('Ошибка гамма коррекции')
            
            elif event == '-HIST_CURRENT-':
                self.show_histogram('current')
            
            elif event == '-HIST_ORIGINAL-':
                self.show_histogram('original')
            
            elif event == '-HIST_COMPARE-':
                self.show_histogram('compare')
            
            elif event == '-COPY_PATH-':
                self.copy_file_path()
            
            elif event == '-COPY_NAME-':
                self.copy_file_name()
                
        except Exception as e:
            self.update_status(f'Ошибка: {str(e)}')
