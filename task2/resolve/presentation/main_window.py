import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from domain.entities import Image as DomainImage, StructuralElement
from domain.repositories import ImageRepository
from application.use_cases import (
    LoadImageUseCase,
    SaveImageUseCase,
    ApplyMorphologicalOperationUseCase
)
from infrastructure.image_repository import OpenCVImageRepository
from infrastructure.morphological_operations import (
    ErosionOperation,
    DilationOperation,
    OpeningOperation,
    ClosingOperation,
    GradientOperation,
    TopHatOperation,
    BlackHatOperation
)


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Морфологические операции")
        self.root.geometry("1200x800")
        
        self.current_image: DomainImage = None
        self.current_result: DomainImage = None
        self.image_repository: ImageRepository = OpenCVImageRepository()
        
        self.load_use_case = LoadImageUseCase(self.image_repository)
        self.save_use_case = SaveImageUseCase(self.image_repository)
        
        self._setup_ui()
    
    def _setup_ui(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить", command=self._load_image)
        file_menu.add_command(label="Сохранить", command=self._save_result)
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(left_panel, text="Оригинальное изображение").pack()
        self.original_canvas = tk.Canvas(left_panel, bg="white", width=500, height=500)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(right_panel, text="Результат").pack()
        self.result_canvas = tk.Canvas(right_panel, bg="white", width=500, height=500)
        self.result_canvas.pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="Структурный элемент (размерность):").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.StringVar(value="3")
        size_entry = ttk.Entry(control_frame, textvariable=self.size_var, width=5)
        size_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Установить", command=self._setup_kernel).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Матрица ядра:").pack(side=tk.LEFT, padx=(20, 5))
        self.kernel_text = tk.Text(control_frame, width=30, height=5)
        self.kernel_text.pack(side=tk.LEFT, padx=5)
        self.kernel_text.insert("1.0", "1 1 1\n1 1 1\n1 1 1")
        
        operations_frame = ttk.LabelFrame(self.root, text="Операции", padding="10")
        operations_frame.pack(fill=tk.X, padx=10, pady=5)
        
        operations = [
            ("Эрозия", ErosionOperation()),
            ("Дилатация", DilationOperation()),
            ("Открытие", OpeningOperation()),
            ("Закрытие", ClosingOperation()),
            ("Градиент", GradientOperation()),
            ("Цилиндр", TopHatOperation()),
            ("Чёрная шляпа", BlackHatOperation())
        ]
        
        for op_name, op_instance in operations:
            btn = ttk.Button(operations_frame, text=op_name, 
                           command=lambda o=op_instance, n=op_name: self._apply_operation(o, n))
            btn.pack(side=tk.LEFT, padx=5)
    
    def _setup_kernel(self):
        try:
            size = int(self.size_var.get())
            if size < 1:
                raise ValueError("Размер должен быть больше 0")
            kernel_matrix = np.ones((size, size), dtype=np.uint8)
            self._update_kernel_text(kernel_matrix)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _update_kernel_text(self, kernel: np.ndarray):
        self.kernel_text.delete("1.0", tk.END)
        rows = []
        for row in kernel:
            rows.append(" ".join(map(str, row.tolist())))
        self.kernel_text.insert("1.0", "\n".join(rows))
    
    def _parse_kernel(self) -> StructuralElement:
        try:
            text = self.kernel_text.get("1.0", tk.END).strip()
            rows = []
            for line in text.split('\n'):
                if line.strip():
                    row = [int(x) for x in line.split()]
                    rows.append(row)
            
            if not rows:
                raise ValueError("Матрица не может быть пустой")
            
            kernel = np.array(rows, dtype=np.uint8)
            return StructuralElement(kernel)
        except Exception as e:
            raise ValueError(f"Неверный формат матрицы: {str(e)}")
    
    def _load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if path:
            try:
                self.current_image = self.load_use_case.execute(path)
                self._display_image(self.current_image, self.original_canvas)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
    
    def _save_result(self):
        if self.current_result is None:
            messagebox.showwarning("Предупреждение", "Нет результата для сохранения")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Все файлы", "*.*")]
        )
        if path:
            try:
                self.save_use_case.execute(self.current_result, path)
                messagebox.showinfo("Успех", "Изображение сохранено")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
    
    def _apply_operation(self, operation, name: str):
        if self.current_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
        
        try:
            structural_element = self._parse_kernel()
            use_case = ApplyMorphologicalOperationUseCase(operation)
            self.current_result = use_case.execute(self.current_image, structural_element)
            self._display_image(self.current_result, self.result_canvas)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _display_image(self, image: DomainImage, canvas: tk.Canvas):
        canvas.delete("all")
        
        if image is None:
            return
        
        img = image.data
        
        if len(img.shape) == 2:
            img_pil = Image.fromarray(img, mode='L')
        else:
            img_pil = Image.fromarray(img)
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
        
        img_width, img_height = img_pil.size
        scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        img_pil = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        canvas.image = img_tk
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        canvas.create_image(x, y, anchor=tk.NW, image=img_tk)

