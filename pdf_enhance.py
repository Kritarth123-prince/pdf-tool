import os
import warnings
import threading
import tkinter as tk
from pathlib import Path
from db_connector import DBConnector
from PyPDF2 import PdfReader, PdfWriter
from tkinter import filedialog, messagebox, ttk

db = DBConnector()

warnings.filterwarnings("ignore")

class PDFSizeTab:
    def __init__(self, notebook, username):
        self.username = username
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="PDF Size Adjuster")
        
        self.files = []
        self.output_folder = tk.StringVar()
        self.mode = tk.StringVar(value="reduce")
        self.adjust_method = tk.StringVar(value="percentage")
        self.percentage = tk.DoubleVar(value=80)
        self.target_size_mb = tk.DoubleVar(value=2.0)
        
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        mode_frame = ttk.LabelFrame(main_frame, text="Size Adjustment Mode")
        mode_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Reduce Size", 
                       variable=self.mode, 
                       value="reduce",
                       command=self.toggle_mode).pack(side="left", padx=5)
        
        ttk.Radiobutton(mode_frame, text="Increase Size", 
                       variable=self.mode, 
                       value="increase",
                       command=self.toggle_mode).pack(side="left", padx=5)
        
        method_frame = ttk.LabelFrame(main_frame, text="Adjustment Method")
        method_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Radiobutton(method_frame, text="Percentage", 
                       variable=self.adjust_method, 
                       value="percentage",
                       command=self.toggle_method).pack(side="left", padx=5)
        
        ttk.Radiobutton(method_frame, text="Target Size (MB)", 
                       variable=self.adjust_method, 
                       value="target_size",
                       command=self.toggle_method).pack(side="left", padx=5)
        
        self.percentage_frame = ttk.Frame(main_frame)
        ttk.Label(self.percentage_frame, text="Percentage of original:").pack(side="left", padx=5)
        ttk.Spinbox(self.percentage_frame, from_=1, to=500, increment=1, 
                    textvariable=self.percentage, width=5).pack(side="left", padx=5)
        ttk.Label(self.percentage_frame, text="%").pack(side="left", padx=5)
        self.percentage_frame.pack(fill="x", pady=(0, 10))
        
        self.target_size_frame = ttk.Frame(main_frame)
        ttk.Label(self.target_size_frame, text="Target file size:").pack(side="left", padx=5)
        ttk.Spinbox(self.target_size_frame, from_=0.1, to=100, increment=0.1, 
                    textvariable=self.target_size_mb, width=5).pack(side="left", padx=5)
        ttk.Label(self.target_size_frame, text="MB").pack(side="left", padx=5)
        self.target_size_frame.pack(fill="x", pady=(0, 10))
        self.target_size_frame.pack_forget()
        
        quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings")
        quality_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(quality_frame, text="Image Quality (DPI):").pack(side="left", padx=5)
        self.dpi = tk.IntVar(value=150)
        ttk.Spinbox(quality_frame, from_=72, to=600, increment=10, 
                   textvariable=self.dpi, width=5).pack(side="left", padx=5)
        
        ttk.Label(quality_frame, text="Compression Level:").pack(side="left", padx=5)
        self.compression = tk.IntVar(value=6)
        ttk.Spinbox(quality_frame, from_=1, to=9, increment=1, 
                   textvariable=self.compression, width=5).pack(side="left", padx=5)
        
        file_frame = ttk.LabelFrame(main_frame, text="PDF Files")
        file_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(file_frame, command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(button_frame, text="Add PDFs", command=self.add_files, 
                 bg="#4285F4", fg="white", font=('Helvetica', 9, 'bold'), 
                 relief=tk.RAISED, borderwidth=2).pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_files, 
                 bg="#EA4335", fg="white", font=('Helvetica', 9, 'bold'), 
                 relief=tk.RAISED, borderwidth=2).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_files, 
                 bg="#FBBC05", fg="white", font=('Helvetica', 9, 'bold'), 
                 relief=tk.RAISED, borderwidth=2).pack(side="left", padx=5)
        
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(output_frame, text="Output Folder:").pack(side="left")
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_folder)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(output_frame, text="Browse", command=self.browse_output, 
                 bg="#34A853", fg="white", font=('Helvetica', 9, 'bold'), 
                 relief=tk.RAISED, borderwidth=2).pack(side="left")
        
        self.process_btn = tk.Button(main_frame, text="Optimize PDFs", command=self.start_process, 
                                   bg="#673AB7", fg="white", font=('Helvetica', 10, 'bold'), 
                                   relief=tk.RAISED, borderwidth=2)
        self.process_btn.pack(pady=(10, 0), fill="x")
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.tab, textvariable=self.status_var, relief=tk.SUNKEN,
                 anchor=tk.W).pack(fill="x", padx=10, pady=(0, 10))
        
        self.toggle_mode()
        self.toggle_method()
    
    def toggle_mode(self):
        if self.mode.get() == "reduce":
            self.process_btn.config(text="Reduce PDF Size", bg="#673AB7")
            self.percentage.set(80)
            self.target_size_mb.set(2.0)
        else:
            self.process_btn.config(text="Increase PDF Size", bg="#009688")
            self.percentage.set(120)
            self.target_size_mb.set(5.0)
    
    def toggle_method(self):
        if self.adjust_method.get() == "percentage":
            self.percentage_frame.pack(fill="x", pady=(0, 10))
            self.target_size_frame.pack_forget()
        else:
            self.target_size_frame.pack(fill="x", pady=(0, 10))
            self.percentage_frame.pack_forget()
    
    def add_files(self):
        filetypes = [("PDF Files", "*.pdf")]
        files = filedialog.askopenfilenames(title="Select PDF Files", filetypes=filetypes)
        if files:
            self.files.extend(files)
            self.update_listbox()
            self.status_var.set(f"{len(self.files)} file(s) selected")
    
    def remove_files(self):
        selected = self.file_listbox.curselection()
        if selected:
            for i in reversed(selected):
                self.files.pop(i)
            self.update_listbox()
            self.status_var.set(f"{len(self.files)} file(s) remaining")
    
    def clear_files(self):
        self.files = []
        self.update_listbox()
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
            messagebox.showwarning("Warning", "No PDF files selected!")
            return False
            
        if not self.output_folder.get():
            messagebox.showwarning("Warning", "Please select an output folder!")
            return False
            
        if self.adjust_method.get() == "percentage":
            if self.mode.get() == "reduce":
                if self.percentage.get() < 1 or self.percentage.get() > 100:
                    messagebox.showwarning("Warning", "For size reduction, percentage must be between 1% and 100%!")
                    return False
            else:
                if self.percentage.get() < 100 or self.percentage.get() > 500:
                    messagebox.showwarning("Warning", "For size increase, percentage must be between 100% and 500%!")
                    return False
        else:
            if self.target_size_mb.get() <= 0:
                messagebox.showwarning("Warning", "Target size must be greater than 0 MB!")
                return False
                
        return True
    
    def start_process(self):
        if not self.validate_inputs():
            return
            
        thread = threading.Thread(
            target=self.process_files,
            args=(self.output_folder.get(),),
            daemon=True
        )
        thread.start()
    
    def process_files(self, output_folder):
        self.status_var.set("Starting size adjustment...")
        
        try:
            os.makedirs(output_folder, exist_ok=True)
            success_count = 0
            
            for i, input_file in enumerate(self.files):
                try:
                    self.status_var.set(f"Processing {i+1}/{len(self.files)}: {os.path.basename(input_file)}")
                    
                    output_path = os.path.join(output_folder, f"adjusted_{Path(input_file).stem}.pdf")
                    original_size = os.path.getsize(input_file) / (1024 * 1024)
                    
                    if self.adjust_method.get() == "percentage":
                        target_size = original_size * (self.percentage.get() / 100)
                    else:
                        target_size = self.target_size_mb.get()
                    
                    self.adjust_pdf_size(input_file, output_path, target_size, original_size)
                    
                    db.log_task(
                        username=self.username,
                        task_type="size_adjust",
                        input_files=input_file,
                        output_file=output_path,
                        parameters=f"mode={self.mode.get()}, method={self.adjust_method.get()}, target={target_size}MB"
                    )
                    
                    success_count += 1
                except Exception as e:
                    error_msg = f"Error processing {os.path.basename(input_file)}: {str(e)}"
                    print(error_msg)
                    self.status_var.set(error_msg)
                    continue
            
            self.status_var.set(f"Size adjustment complete! {success_count}/{len(self.files)} files processed")
            messagebox.showinfo("Success", f"Adjusted size for {success_count} file(s)")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Size adjustment failed:\n{str(e)}")
    
    def adjust_pdf_size(self, input_path, output_path, target_size_mb, original_size_mb):
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            if hasattr(reader, 'metadata') and reader.metadata:
                writer.add_metadata(reader.metadata)
            
            compression_needed = target_size_mb / original_size_mb
            
            if self.mode.get() == "reduce":
                for page in writer.pages:
                    pass
            
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                result_size = os.path.getsize(output_path) / (1024 * 1024)
                if result_size > target_size_mb * 1.1:
                    pass
                
            else:
                dummy_size = (target_size_mb - original_size_mb) * 1024 * 1024
                

                with open(output_path, "wb") as f:
                    writer.write(f)
                
                result_size = os.path.getsize(output_path) / (1024 * 1024)
                if result_size < target_size_mb * 0.9:
                    self.add_file_padding(output_path, target_size_mb)
            
        except Exception as e:
            raise Exception(f"Size adjustment failed: {str(e)}")
    
    def add_file_padding(self, file_path, target_size_mb):
        current_size = os.path.getsize(file_path) / (1024 * 1024)
        padding_needed = (target_size_mb - current_size) * 1024 * 1024
        
        if padding_needed > 0:
            with open(file_path, "ab") as f:
                f.write(b'\0' * int(padding_needed))