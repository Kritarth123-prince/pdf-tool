import os
import threading
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from db_connector import DBConnector
from tkinter import filedialog, messagebox, ttk

db = DBConnector()

class ImageResizerTab:
    def __init__(self, notebook, username):
        self.username = username
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Image Resizer")
        
        self.files = []
        self.output_folder = tk.StringVar()
        self.current_file_index = 0
        self.preview_image = None
        
        self.resize_mode = tk.StringVar(value="reduce")
        self.adjust_method = tk.StringVar(value="percentage")
        self.unit = tk.StringVar(value="pixels")
        self.lock_aspect = tk.BooleanVar(value=True)
        self.percentage = tk.IntVar(value=80)
        self.width = tk.IntVar(value=0)
        self.height = tk.IntVar(value=0)
        
        self.quality = tk.IntVar(value=95)
        self.optimize = tk.BooleanVar(value=True)
        self.keep_metadata = tk.BooleanVar(value=True)
        self.output_format = tk.StringVar(value="original")
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        mode_frame = ttk.LabelFrame(main_frame, text="Resize Mode")
        mode_frame.pack(fill="x", pady=(0, 10))
        ttk.Radiobutton(mode_frame, text="Reduce Size", variable=self.resize_mode,
                        value="reduce", command=self.toggle_mode).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Extend Size", variable=self.resize_mode,
                        value="extend", command=self.toggle_mode).pack(side="left", padx=5)

        method_frame = ttk.LabelFrame(main_frame, text="Adjustment Method")
        method_frame.pack(fill="x", pady=(0, 10))
        ttk.Radiobutton(method_frame, text="Percentage", variable=self.adjust_method,
                        value="percentage", command=self.toggle_method).pack(side="left", padx=5)
        ttk.Radiobutton(method_frame, text="Exact Dimensions", variable=self.adjust_method,
                        value="dimensions", command=self.toggle_method).pack(side="left", padx=5)

        unit_frame = ttk.Frame(main_frame)
        unit_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(unit_frame, text="Unit:").pack(side="left", padx=5)
        for unit in ["pixels", "cm", "inches", "mm"]:
            ttk.Radiobutton(unit_frame, text=unit, variable=self.unit, value=unit,
                            command=self.update_dimensions).pack(side="left", padx=5)

        self.percentage_frame = ttk.Frame(main_frame)
        ttk.Label(self.percentage_frame, text="Scale to:").pack(side="left", padx=5)
        ttk.Spinbox(self.percentage_frame, from_=1, to=500, increment=1,
                    textvariable=self.percentage, width=5).pack(side="left", padx=5)
        ttk.Label(self.percentage_frame, text="%").pack(side="left", padx=5)
        self.percentage_frame.pack(fill="x", pady=(0, 5))

        self.dimensions_frame = ttk.Frame(main_frame)
        ttk.Checkbutton(self.dimensions_frame, text="Lock aspect ratio",
                        variable=self.lock_aspect).grid(row=0, column=0, columnspan=2, sticky="w", padx=5)
        ttk.Label(self.dimensions_frame, text="Width:").grid(row=1, column=0, sticky="e", padx=5)
        ttk.Entry(self.dimensions_frame, textvariable=self.width, width=8).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(self.dimensions_frame, text="Height:").grid(row=2, column=0, sticky="e", padx=5)
        ttk.Entry(self.dimensions_frame, textvariable=self.height, width=8).grid(row=2, column=1, sticky="w", padx=5)
        self.dimensions_frame.pack_forget()

        preview_file_frame = ttk.LabelFrame(main_frame, text="Image Preview & Files")
        preview_file_frame.pack(fill="both", expand=True, pady=(10, 0))

        file_frame = ttk.Frame(preview_file_frame)
        file_frame.pack(side="left", fill="both", expand=True)
        ttk.Label(file_frame, text="Image Files").pack(anchor="w", padx=5, pady=(0, 2))
        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        scrollbar = ttk.Scrollbar(file_frame, command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        self.preview_canvas = tk.Canvas(preview_file_frame, bg="white", width=400, height=300)
        self.preview_canvas.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        tk.Button(button_frame, text="Add Images", command=self.add_files,
                bg="#4285F4", fg="white", font=('Helvetica', 9, 'bold')).pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_files,
                bg="#EA4335", fg="white", font=('Helvetica', 9, 'bold')).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_files,
                bg="#FBBC05", fg="white", font=('Helvetica', 9, 'bold')).pack(side="left", padx=5)

        quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings")
        quality_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(quality_frame, text="Quality (1-100):").pack(side="left", padx=5)
        ttk.Spinbox(quality_frame, from_=1, to=100, increment=1,
                    textvariable=self.quality, width=5).pack(side="left", padx=5)
        ttk.Checkbutton(quality_frame, text="Optimize", variable=self.optimize).pack(side="left", padx=10)
        ttk.Checkbutton(quality_frame, text="Keep Metadata", variable=self.keep_metadata).pack(side="left", padx=10)

        format_frame = ttk.LabelFrame(main_frame, text="Output Format")
        format_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(format_frame, text="Format:").pack(side="left", padx=5)
        ttk.OptionMenu(format_frame, self.output_format, "original", "JPEG", "PNG", "WEBP", "BMP").pack(side="left", padx=5)

        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(output_frame, text="Output Folder:").pack(side="left")
        ttk.Entry(output_frame, textvariable=self.output_folder).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(output_frame, text="Browse", command=self.browse_output,
                bg="#34A853", fg="white", font=('Helvetica', 9, 'bold')).pack(side="left")

        self.process_btn = tk.Button(main_frame, text="Resize Images", command=self.start_process,
                                    bg="#673AB7", fg="white", font=('Helvetica', 10, 'bold'))
        self.process_btn.pack(pady=(10, 0), fill="x")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.tab, textvariable=self.status_var, relief=tk.SUNKEN,
                anchor=tk.W).pack(fill="x", padx=10, pady=(0, 10))

        self.toggle_mode()
        self.toggle_method()

    def toggle_mode(self):
        if self.resize_mode.get() == "reduce":
            self.process_btn.config(text="Reduce Images", bg="#673AB7")
            self.percentage.set(80)
        else:
            self.process_btn.config(text="Extend Images", bg="#009688")
            self.percentage.set(120)
    
    def toggle_method(self):
        if self.adjust_method.get() == "percentage":
            self.percentage_frame.pack(fill="x", pady=(0, 5))
            self.dimensions_frame.pack_forget()
        else:
            self.dimensions_frame.pack(fill="x", pady=(0, 5))
            self.percentage_frame.pack_forget()
        self.update_dimensions()
    
    def on_file_select(self, event):
        selected = self.file_listbox.curselection()
        if selected:
            self.current_file_index = selected[0]
            self.update_preview()
            self.update_dimensions()
    
    def update_preview(self):
        self.preview_canvas.delete("all")
        if self.files and self.current_file_index < len(self.files):
            try:
                img = Image.open(self.files[self.current_file_index])
                img.thumbnail((400, 300))
                self.preview_image = ImageTk.PhotoImage(img)
                self.preview_canvas.create_image(200, 150, image=self.preview_image, anchor=tk.CENTER)
                self.status_var.set(f"Preview: {os.path.basename(self.files[self.current_file_index])}")
            except Exception as e:
                self.preview_canvas.create_text(200, 150, text="Invalid image", fill="red", anchor=tk.CENTER)
                self.status_var.set(f"Error loading image: {e}")

    def update_dimensions(self):
        if self.files and self.current_file_index < len(self.files):
            try:
                img = Image.open(self.files[self.current_file_index])
                width, height = img.size
                
                if self.unit.get() != "pixels":
                    dpi = 96
                    inches_w = width / dpi
                    inches_h = height / dpi
                    
                    if self.unit.get() == "cm":
                        width = inches_w * 2.54
                        height = inches_h * 2.54
                    elif self.unit.get() == "mm":
                        width = inches_w * 25.4
                        height = inches_h * 25.4
                    else:
                        width = inches_w
                        height = inches_h
                
                self.width.set(round(width, 2))
                self.height.set(round(height, 2))
            except Exception as e:
                print(f"Error updating dimensions: {e}")
    
    def add_files(self):
        filetypes = [
            ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("All Files", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Select Image Files", filetypes=filetypes)
        if files:
            self.files.extend(files)
            self.update_listbox()
            if len(self.files) == len(files):
                self.current_file_index = 0
                self.update_preview()
                self.update_dimensions()
            self.status_var.set(f"{len(self.files)} file(s) selected")
    
    def remove_files(self):
        selected = self.file_listbox.curselection()
        if selected:
            for i in reversed(selected):
                self.files.pop(i)
            self.update_listbox()
            if self.files:
                self.current_file_index = min(self.current_file_index, len(self.files)-1)
                self.update_preview()
                self.update_dimensions()
            self.status_var.set(f"{len(self.files)} file(s) remaining")
    
    def clear_files(self):
        self.files = []
        self.update_listbox()
        self.preview_canvas.delete("all")
        self.status_var.set("File list cleared")
    
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def update_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def validate_inputs(self):
        if not self.files:
            messagebox.showwarning("Warning", "No image files selected!")
            return False
            
        if not self.output_folder.get():
            messagebox.showwarning("Warning", "Please select an output folder!")
            return False
            
        if self.adjust_method.get() == "percentage":
            if self.resize_mode.get() == "reduce" and (self.percentage.get() <= 0 or self.percentage.get() > 100):
                messagebox.showwarning("Warning", "For reduction, percentage must be between 1-100!")
                return False
            elif self.resize_mode.get() == "extend" and self.percentage.get() < 100:
                messagebox.showwarning("Warning", "For extension, percentage must be ≥100!")
                return False
        else:
            if self.width.get() <= 0 or self.height.get() <= 0:
                messagebox.showwarning("Warning", "Dimensions must be greater than 0!")
                return False
                
        return True
    
    def start_process(self):
        if not self.validate_inputs():
            return
            
        thread = threading.Thread(
            target=self.process_images,
            args=(self.output_folder.get(),),
            daemon=True
        )
        thread.start()
    
    def process_images(self, output_folder):
        self.status_var.set("Starting image processing...")
        
        try:
            os.makedirs(output_folder, exist_ok=True)
            success_count = 0
            
            for i, input_file in enumerate(self.files):
                try:
                    self.status_var.set(f"Processing {i+1}/{len(self.files)}: {os.path.basename(input_file)}")
                    
                    if self.output_format.get() == "original":
                        ext = Path(input_file).suffix
                        output_path = os.path.join(output_folder, f"resized_{Path(input_file).stem}{ext}")
                    else:
                        output_path = os.path.join(output_folder, f"resized_{Path(input_file).stem}.{self.output_format.get().lower()}")
                    
                    self.resize_image(input_file, output_path)
                    
                    db.log_task(
                        username=self.username,
                        task_type="image_resize",
                        input_files=input_file,
                        output_file=output_path,
                        parameters=f"mode={self.resize_mode.get()}, method={self.adjust_method.get()}"
                    )
                    
                    success_count += 1
                except Exception as e:
                    error_msg = f"Error processing {os.path.basename(input_file)}: {str(e)}"
                    print(error_msg)
                    self.status_var.set(error_msg)
                    continue
            
            self.status_var.set(f"Processing complete! {success_count}/{len(self.files)} files processed")
            messagebox.showinfo("Success", f"Processed {success_count} image(s)")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Processing failed:\n{str(e)}")
    
    def resize_image(self, input_path, output_path):
        try:
            img = Image.open(input_path)

            if self.adjust_method.get() == "percentage":
                scale = self.percentage.get() / 100
                width = int(img.width * scale)
                height = int(img.height * scale)
            else:
                width = self.width.get()
                height = self.height.get()
                if self.unit.get() != "pixels":
                    dpi = 96
                    if self.unit.get() == "cm":
                        width = int(width / 2.54 * dpi)
                        height = int(height / 2.54 * dpi)
                    elif self.unit.get() == "mm":
                        width = int(width / 25.4 * dpi)
                        height = int(height / 25.4 * dpi)
                    elif self.unit.get() == "inches":
                        width = int(width * dpi)
                        height = int(height * dpi)

                if self.lock_aspect.get():
                    orig_ratio = img.width / img.height
                    if width / height > orig_ratio:
                        width = int(height * orig_ratio)
                    else:
                        height = int(width / orig_ratio)

            img = img.resize((width, height), Image.LANCZOS)

            save_kwargs = {
                "quality": self.quality.get(),
                "optimize": self.optimize.get(),
            }

            if not self.keep_metadata.get():
                img.info.pop("exif", None)

            img_format = self.output_format.get()
            if img_format == "original":
                img_format = img.format or "JPEG"

            img.save(output_path, format=img_format.upper(), **save_kwargs)

        except Exception as e:
            raise RuntimeError(f"Resize failed for {input_path}: {str(e)}")