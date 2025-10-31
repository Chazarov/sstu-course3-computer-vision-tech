import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from domain.entities import Image as DomainImage, StructuralElement
from application.use_cases import LoadImageUseCase, SaveImageUseCase, ApplyMorphologicalOperationUseCase
from infrastructure.image_repository import OpenCVImageRepository
from infrastructure.morphological_operations import (
    OpenCVErosionOperation,
    OpenCVDilationOperation,
    OpenCVOpeningOperation,
    OpenCVClosingOperation,
    OpenCVGradientOperation,
    OpenCVTopHatOperation,
    OpenCVBlackHatOperation
)


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Морфологические операции")
        
        self.current_image = None
        self.original_image = None
        self.repository = OpenCVImageRepository()
        self.load_use_case = LoadImageUseCase(self.repository)
        self.save_use_case = SaveImageUseCase(self.repository)
        
        self.operations_map = {
            "Эрозия": OpenCVErosionOperation(),
            "Дилатация": OpenCVDilationOperation(),
            "Открытие": OpenCVOpeningOperation(),
            "Закрытие": OpenCVClosingOperation(),
            "Градиент": OpenCVGradientOperation(),
            "Цилиндр": OpenCVTopHatOperation(),
            "Чёрная шляпа": OpenCVBlackHatOperation()
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(control_frame, text="Загрузить", command=self.load_image).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Сохранить", command=self.save_image).grid(row=0, column=1, padx=5)
        
        self.show_original_btn = ttk.Button(control_frame, text="Посмотреть оригинал")
        self.show_original_btn.grid(row=0, column=2, padx=5)
        self.show_original_btn.bind("<Button-1>", self.on_show_original_press)
        self.show_original_btn.bind("<ButtonRelease-1>", self.on_show_original_release)
        self.show_original_btn.state(['disabled'])
        
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        
        canvas_frame = ttk.Frame(image_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar_v = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_h = ttk.Scrollbar(image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        operations_frame = ttk.LabelFrame(main_frame, text="Операции", padding="10")
        operations_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(operations_frame, text="Операция:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.operation_var = tk.StringVar(value="Эрозия")
        operation_combo = ttk.Combobox(operations_frame, textvariable=self.operation_var, 
                                      values=list(self.operations_map.keys()), state="readonly", width=15)
        operation_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        kernel_frame = ttk.LabelFrame(main_frame, text="Структурный элемент", padding="10")
        kernel_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(kernel_frame, text="Размерность (строки x столбцы):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        size_frame = ttk.Frame(kernel_frame)
        size_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.rows_var = tk.StringVar(value="3")
        self.cols_var = tk.StringVar(value="3")
        ttk.Spinbox(size_frame, from_=1, to=20, textvariable=self.rows_var, width=5).grid(row=0, column=0, padx=2)
        ttk.Label(size_frame, text="x").grid(row=0, column=1, padx=2)
        ttk.Spinbox(size_frame, from_=1, to=20, textvariable=self.cols_var, width=5).grid(row=0, column=2, padx=2)
        ttk.Button(size_frame, text="Создать матрицу", command=self.create_kernel_matrix).grid(row=0, column=3, padx=5)
        
        self.kernel_entries_frame = ttk.Frame(kernel_frame)
        self.kernel_entries_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(kernel_frame, text="Применить операцию", command=self.apply_operation).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.create_kernel_matrix()
    
    def create_kernel_matrix(self):
        for widget in self.kernel_entries_frame.winfo_children():
            widget.destroy()
        
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            
            if rows < 1 or cols < 1 or rows > 20 or cols > 20:
                messagebox.showerror("Ошибка", "Размерность должна быть от 1 до 20")
                return
            
            self.kernel_entries = []
            for i in range(rows):
                row_entries = []
                for j in range(cols):
                    entry = ttk.Entry(self.kernel_entries_frame, width=5)
                    entry.insert(0, "1")
                    entry.grid(row=i, column=j, padx=2, pady=2)
                    row_entries.append(entry)
                self.kernel_entries.append(row_entries)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение размерности")
    
    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if path:
            try:
                loaded_image = self.load_use_case.execute(path)
                self.original_image = DomainImage(np.copy(loaded_image.data))
                self.current_image = loaded_image
                self.display_image(self.current_image)
                self.show_original_btn.state(['!disabled'])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")
    
    def save_image(self):
        if self.current_image is None:
            messagebox.showwarning("Предупреждение", "Нет изображения для сохранения")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Все файлы", "*.*")]
        )
        if path:
            try:
                self.save_use_case.execute(self.current_image, path)
                messagebox.showinfo("Успех", "Изображение сохранено")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")
    
    def display_image(self, image: DomainImage):
        self.canvas.delete("all")
        
        pil_image = Image.fromarray(image.data)
        
        max_width = 800
        max_height = 600
        
        width, height = pil_image.size
        scale = min(max_width / width, max_height / height, 1.0)
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        self.photo = ImageTk.PhotoImage(pil_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def get_kernel_from_entries(self):
        try:
            rows = len(self.kernel_entries)
            cols = len(self.kernel_entries[0]) if rows > 0 else 0
            
            kernel = np.zeros((rows, cols), dtype=np.uint8)
            for i in range(rows):
                for j in range(cols):
                    value = int(self.kernel_entries[i][j].get())
                    kernel[i, j] = value
            
            return kernel
        except (ValueError, IndexError) as e:
            raise ValueError("Некорректные значения в матрице структурного элемента")
    
    def apply_operation(self):
        if self.current_image is None:
            messagebox.showwarning("Предупреждение", "Загрузите изображение")
            return
        
        try:
            kernel = self.get_kernel_from_entries()
            structural_element = StructuralElement(kernel)
            
            operation_name = self.operation_var.get()
            operation = self.operations_map[operation_name]
            
            use_case = ApplyMorphologicalOperationUseCase(operation)
            self.current_image = use_case.execute(self.current_image, structural_element)
            self.display_image(self.current_image)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить операцию: {str(e)}")
    
    def on_show_original_press(self, event):
        if self.original_image is not None:
            self.display_image(self.original_image)
    
    def on_show_original_release(self, event):
        if self.current_image is not None:
            self.display_image(self.current_image)


def main():
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()

