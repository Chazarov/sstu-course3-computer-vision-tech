"""
Графический интерфейс приложения на основе FreeSimpleGUI.
"""
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
        
        # Параметры обработки
        self._processing_params = ImageProcessingParameters()
        
        # Настройка темы
        sg.theme('LightBlue3')
        
        # Типы файлов для диалогов
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
                [sg.Text('Путь к файлу:', size=(15, 1)), sg.Text('', key='-FILE_PATH-', size=(25, 1))],
                [sg.Text('Имя файла:', size=(15, 1)), sg.Text('', key='-FILE_NAME-', size=(25, 1))],
            ], font=('Arial', 10), pad=(5, 5))],
            [sg.Frame('EXIF данные', [
                [sg.Multiline('', key='-EXIF_INFO-', size=(40, 8), disabled=True, 
                             font=('Courier', 9), background_color='#f0f0f0')]
            ], font=('Arial', 10), pad=(5, 5))],
            [sg.HorizontalSeparator()],
            [sg.Text('Гистограмма:', font=('Arial', 11, 'bold'))],
            [
                sg.Button('Показать текущую', key='-HIST_CURRENT-', size=(15, 2), disabled=True),
                sg.Button('Показать оригинальную', key='-HIST_ORIGINAL-', size=(15, 2), disabled=True)
            ],
            [
                sg.Button('Сравнить гистограммы', key='-HIST_COMPARE-', size=(15, 2), disabled=True)
            ]
        ]
        
        # Колонка с параметрами обработки
        processing_column = [
            [sg.Text('Параметры обработки:', font=('Arial', 12, 'bold'))],
            [
                sg.Text('Яркость:', size=(12, 1)),
                sg.Slider(range=(-100, 100), default_value=0, orientation='h', 
                         size=(20, 15), key='-BRIGHTNESS-', enable_events=True)
            ],
            [
                sg.Text('Контрастность:', size=(12, 1)),
                sg.Slider(range=(0.1, 3.0), default_value=1.0, resolution=0.1, orientation='h',
                         size=(20, 15), key='-CONTRAST-', enable_events=True)
            ],
            [
                sg.Text('Насыщенность:', size=(12, 1)),
                sg.Slider(range=(0.0, 3.0), default_value=1.0, resolution=0.1, orientation='h',
                         size=(20, 15), key='-SATURATION-', enable_events=True)
            ],
            [sg.HorizontalSeparator()],
            [sg.Text('Преобразования:', font=('Arial', 11, 'bold'))],
            [
                sg.Button('В градации серого', key='-GRAYSCALE-', size=(18, 1), disabled=True),
                sg.Button('Повернуть на 90°', key='-ROTATE-', size=(18, 1), disabled=True)
            ],
            [sg.HorizontalSeparator()],
            [sg.Text('Коррекция ч/б изображения:', font=('Arial', 11, 'bold'))],
            [
                sg.Text('Мин:', size=(4, 1)),
                sg.Input('0', key='-LINEAR_MIN-', size=(6, 1)),
                sg.Text('Макс:', size=(4, 1)),
                sg.Input('255', key='-LINEAR_MAX-', size=(6, 1)),
                sg.Button('Линейная', key='-LINEAR_CORRECT-', size=(10, 1), disabled=True)
            ],
            [
                sg.Text('Гамма:', size=(6, 1)),
                sg.Slider(range=(0.1, 3.0), default_value=1.0, resolution=0.1, orientation='h',
                         size=(15, 15), key='-GAMMA-'),
                sg.Button('Нелинейная', key='-NONLINEAR_CORRECT-', size=(10, 1), disabled=True)
            ]
        ]
        
        # Основной макет
        layout = [
            [
                sg.Column(image_column, vertical_alignment='top'),
                sg.VerticalSeparator(),
                sg.Column([
                    [sg.Column(info_column, vertical_alignment='top')],
                    [sg.HorizontalSeparator()],
                    [sg.Column(processing_column, vertical_alignment='top')]
                ], vertical_alignment='top')
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
            resizable=False,
            location=(100, 50)
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
                # Обновляем основные параметры
                self._window['-FILE_SIZE-'].update(info.get('Размер файла', ''))
                self._window['-RESOLUTION-'].update(info.get('Разрешение', ''))
                self._window['-COLOR_DEPTH-'].update(info.get('Глубина цвета', ''))
                self._window['-FORMAT-'].update(info.get('Формат файла', ''))
                self._window['-COLOR_MODEL-'].update(info.get('Цветовая модель', ''))
                self._window['-MODIFIED-'].update(info.get('Модифицировано', ''))
                
                # Обновляем дополнительную информацию
                file_path = info.get('Путь к файлу', '')
                # Сокращаем длинный путь для красивого отображения
                if len(file_path) > 40:
                    file_path = '...' + file_path[-37:]
                self._window['-FILE_PATH-'].update(file_path)
                self._window['-FILE_NAME-'].update(info.get('Имя файла', ''))
                
                # Формируем EXIF информацию
                exif_lines = []
                for key, value in info.items():
                    if key.startswith('EXIF:'):
                        exif_key = key.replace('EXIF: ', '')
                        # Ограничиваем длину строки для красивого отображения
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
        
        # Очищаем основные параметры
        self._window['-FILE_SIZE-'].update('')
        self._window['-RESOLUTION-'].update('')
        self._window['-COLOR_DEPTH-'].update('')
        self._window['-FORMAT-'].update('')
        self._window['-COLOR_MODEL-'].update('')
        self._window['-MODIFIED-'].update('')
        
        # Очищаем дополнительную информацию
        self._window['-FILE_PATH-'].update('')
        self._window['-FILE_NAME-'].update('')
        
        # Очищаем EXIF данные
        self._window['-EXIF_INFO-'].update('')
    
    def enable_image_controls(self, enabled: bool) -> None:
        """Включает/выключает элементы управления изображением"""
        if not self._window:
            return
        
        controls = [
            '-SAVE-', '-RESET-', '-GRAYSCALE-', '-ROTATE-',
            '-HIST_CURRENT-', '-HIST_ORIGINAL-', '-HIST_COMPARE-'
        ]
        
        for control in controls:
            self._window[control].update(disabled=not enabled)
        
        # Коррекция доступна только для ч/б изображений
        is_grayscale = (enabled and 
                       self._image_service.current_image and 
                       self._image_service.current_image.is_grayscale())
        
        self._window['-LINEAR_CORRECT-'].update(disabled=not is_grayscale)
        self._window['-NONLINEAR_CORRECT-'].update(disabled=not is_grayscale)
    
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
        
        self._window['-BRIGHTNESS-'].update(0)
        self._window['-CONTRAST-'].update(1.0)
        self._window['-SATURATION-'].update(1.0)
        self._window['-GAMMA-'].update(1.0)
        self._processing_params = ImageProcessingParameters()
    
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
            
            # Создаем окно с двумя гистограммами
            current_bytes = self._image_service.plot_histogram(current_hist, '(Текущее)')
            original_bytes = self._image_service.plot_histogram(original_hist, '(Оригинальное)')
            
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
        """Создает окно сравнения гистограмм"""
        layout = [
            [sg.Text('Оригинальная гистограмма:', font=('Arial', 12, 'bold'))],
            [sg.Image(data=original_bytes)],
            [sg.Text('Текущая гистограмма:', font=('Arial', 12, 'bold'))],
            [sg.Image(data=current_bytes)],
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
                # Обрабатываем события главного окна
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
            
            elif event in ['-BRIGHTNESS-', '-CONTRAST-', '-SATURATION-']:
                # Обновляем параметры из слайдеров
                self._processing_params.brightness = values['-BRIGHTNESS-']
                self._processing_params.contrast = values['-CONTRAST-']
                self._processing_params.saturation = values['-SATURATION-']
                self.apply_processing_params()
            
            elif event == '-LINEAR_CORRECT-':
                try:
                    min_val = int(values['-LINEAR_MIN-'])
                    max_val = int(values['-LINEAR_MAX-'])
                    if self._image_service.apply_linear_correction(min_val, max_val):
                        self.update_image_display()
                        self.update_status('Линейная коррекция применена')
                    else:
                        self.update_status('Ошибка линейной коррекции')
                except ValueError:
                    self.update_status('Неверные значения для линейной коррекции')
            
            elif event == '-NONLINEAR_CORRECT-':
                gamma = values['-GAMMA-']
                if self._image_service.apply_nonlinear_correction(gamma):
                    self.update_image_display()
                    self.update_status('Нелинейная коррекция применена')
                else:
                    self.update_status('Ошибка нелинейной коррекции')
            
            elif event == '-HIST_CURRENT-':
                self.show_histogram('current')
            
            elif event == '-HIST_ORIGINAL-':
                self.show_histogram('original')
            
            elif event == '-HIST_COMPARE-':
                self.show_histogram('compare')
                
        except Exception as e:
            self.update_status(f'Ошибка: {str(e)}')
