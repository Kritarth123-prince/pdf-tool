import io
import os
import threading
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from db_connector import DBConnector
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from tkinter import filedialog, messagebox, ttk, colorchooser

db = DBConnector()

class PDFWatermarkTab:
    def __init__(self, notebook, username):
        self.username = username
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="PDF Watermark")
        
        self.watermark_type = tk.StringVar(value="text")
        self.watermark_color = (0, 0, 0)
        self.selected_image = None
        self.transparency = tk.DoubleVar(value=50.0)
        self.rotation = tk.IntVar(value=45)
        self.start_page = tk.IntVar(value=1)
        self.end_page = tk.IntVar(value=1)
        self.layer_position = tk.StringVar(value="over")
        self.font_size = tk.IntVar(value=36)
        self.font_family = tk.StringVar(value="Helvetica")
        self.bold_style = tk.BooleanVar(value=False)
        self.italic_style = tk.BooleanVar(value=False)
        self.underline_style = tk.BooleanVar(value=False)
        self.watermark_position = tk.StringVar(value="center")
        self.image_scale = tk.DoubleVar(value=100.0)
        self.image_aspect = tk.BooleanVar(value=True)
        
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        type_frame = ttk.LabelFrame(main_frame, text="Watermark Type")
        type_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Radiobutton(type_frame, text="Text Watermark", 
                       variable=self.watermark_type, 
                       value="text",
                       command=self.toggle_watermark_type).pack(side="left", padx=5)
        
        ttk.Radiobutton(type_frame, text="Image Watermark", 
                       variable=self.watermark_type, 
                       value="image",
                       command=self.toggle_watermark_type).pack(side="left", padx=5)
        
        self.text_frame = ttk.LabelFrame(main_frame, text="Text Watermark Options")
        
        ttk.Label(self.text_frame, text="Text:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.text_entry = ttk.Entry(self.text_frame, width=40)
        self.text_entry.grid(row=0, column=1, columnspan=4, sticky="ew", padx=5, pady=2)
        self.text_entry.insert(0, "Confidential")
        
        ttk.Label(self.text_frame, text="Font:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.font_combo = ttk.Combobox(self.text_frame, textvariable=self.font_family, 
                                     values=["Helvetica", "Times-Roman", "Courier", 
                                             "Helvetica-Bold", "Times-Bold", "Courier-Bold",
                                             "Helvetica-Oblique", "Times-Italic", "Courier-Oblique",
                                             "Helvetica-BoldOblique", "Times-BoldItalic", "Courier-BoldOblique"])
        self.font_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.text_frame, text="Size:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        ttk.Spinbox(self.text_frame, from_=8, to=120, textvariable=self.font_size, width=5).grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        style_frame = ttk.Frame(self.text_frame)
        style_frame.grid(row=1, column=4, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(style_frame, text="Bold", variable=self.bold_style).pack(side="left", padx=2)
        ttk.Checkbutton(style_frame, text="Italic", variable=self.italic_style).pack(side="left", padx=2)
        ttk.Checkbutton(style_frame, text="Underline", variable=self.underline_style).pack(side="left", padx=2)
        
        ttk.Label(self.text_frame, text="Color:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.color_btn = tk.Button(self.text_frame, text="Choose", command=self.choose_color, bg="#4CAF50", fg="white")
        self.color_btn.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.color_preview = tk.Canvas(self.text_frame, width=30, height=20, bg="#000000")
        self.color_preview.grid(row=2, column=2, sticky="w", padx=5, pady=2)
        
        self.image_frame = ttk.LabelFrame(main_frame, text="Image Watermark Options")
        
        ttk.Label(self.image_frame, text="Image:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.image_path_entry = ttk.Entry(self.image_frame, width=30)
        self.image_path_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        tk.Button(self.image_frame, text="Browse", command=self.browse_image, bg="#2196F3", fg="white").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        self.image_preview = tk.Label(self.image_frame)
        self.image_preview.grid(row=1, column=0, columnspan=3, pady=5)
        
        ttk.Label(self.image_frame, text="Scale (%):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Scale(self.image_frame, from_=10, to=200, variable=self.image_scale, 
                 command=lambda v: self.image_scale.set(round(float(v)))).grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self.image_frame, textvariable=self.image_scale).grid(row=2, column=2, sticky="w", padx=5, pady=2)
        
        ttk.Checkbutton(self.image_frame, text="Maintain Aspect Ratio", variable=self.image_aspect).grid(row=3, column=0, columnspan=3, sticky="w", padx=5, pady=2)
        
        position_frame = ttk.LabelFrame(main_frame, text="Watermark Position")
        
        positions = [
            ("Top-Left", "top-left", "#FFCCCC"), ("Top-Center", "top-center", "#CCFFCC"), ("Top-Right", "top-right", "#CCCCFF"),
            ("Center-Left", "center-left", "#FFFFCC"), ("Center", "center", "#FFCCFF"), ("Center-Right", "center-right", "#CCFFFF"),
            ("Bottom-Left", "bottom-left", "#FFE5CC"), ("Bottom-Center", "bottom-center", "#E5CCFF"), ("Bottom-Right", "bottom-right", "#CCE5FF")
        ]
        
        for i, (text, value, color) in enumerate(positions):
            btn = ttk.Radiobutton(
                position_frame, 
                text=text, 
                variable=self.watermark_position, 
                value=value,
                style="Toolbutton"
            )
            btn.grid(row=i//3, column=i%3, sticky="nsew", padx=2, pady=2)
            
            btn.configure(style=f"{value}.TRadiobutton")
            style = ttk.Style()
            style.configure(f"{value}.TRadiobutton", background=color)
            style.map(f"{value}.TRadiobutton",
                     background=[("selected", color), ("active", color)],
                     relief=[("selected", "sunken"), ("!selected", "raised")])
        
        common_frame = ttk.LabelFrame(main_frame, text="Watermark Settings")
        
        ttk.Label(common_frame, text="Transparency (%):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Scale(common_frame, from_=0, to=100, variable=self.transparency, 
                 command=lambda v: self.transparency.set(round(float(v)))).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(common_frame, textvariable=self.transparency).grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(common_frame, text="Rotation (degrees):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Scale(common_frame, from_=0, to=360, variable=self.rotation).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(common_frame, textvariable=self.rotation).grid(row=1, column=2, sticky="w", padx=5, pady=2)
        
        ttk.Label(common_frame, text="Pages:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(common_frame, text="From").grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.start_spin = ttk.Spinbox(common_frame, from_=1, to=999, textvariable=self.start_page, width=5)
        self.start_spin.grid(row=2, column=2, sticky="w", padx=5, pady=2)
        ttk.Label(common_frame, text="To").grid(row=2, column=3, sticky="w", padx=5, pady=2)
        self.end_spin = ttk.Spinbox(common_frame, from_=1, to=999, textvariable=self.end_page, width=5)
        self.end_spin.grid(row=2, column=4, sticky="w", padx=5, pady=2)
        
        ttk.Label(common_frame, text="Layer Position:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(common_frame, text="Over Content", variable=self.layer_position, value="over").grid(row=3, column=1, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(common_frame, text="Under Content", variable=self.layer_position, value="under").grid(row=3, column=2, sticky="w", padx=5, pady=2)
        
        file_frame = ttk.LabelFrame(main_frame, text="PDF Files")
        file_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(file_frame, command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(button_frame, text="Add PDFs", command=self.add_files, bg="#4285F4", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_files, bg="#EA4335", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_files, bg="#FBBC05", fg="white").pack(side="left", padx=5)
        
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(output_frame, text="Output Folder:").pack(side="left")
        self.output_entry = ttk.Entry(output_frame)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(output_frame, text="Browse", command=self.browse_output, bg="#34A853", fg="white").pack(side="left")
        
        tk.Button(main_frame, text="Apply Watermark", command=self.start_watermark, 
                bg="#673AB7", fg="white").pack(pady=(10, 0), fill="x")
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.tab, textvariable=self.status_var, relief=tk.SUNKEN,
                 anchor=tk.W).pack(fill="x", padx=10, pady=(0, 10))
        
        self.files = []
        
        self.toggle_watermark_type()
        position_frame.pack(fill="x", pady=(10, 0))
        common_frame.pack(fill="x", pady=(10, 0))
    
    def toggle_watermark_type(self):
        if self.watermark_type.get() == "text":
            self.text_frame.pack(fill="x", pady=(10, 0))
            self.image_frame.pack_forget()
        else:
            self.image_frame.pack(fill="x", pady=(10, 0))
            self.text_frame.pack_forget()
    
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[1]:
            self.watermark_color = color[0]
            self.color_preview.config(bg=color[1])
    
    def browse_image(self):
        filetypes = [("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        filename = filedialog.askopenfilename(title="Select Watermark Image", filetypes=filetypes)
        if filename:
            self.selected_image = filename
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, filename)
            
            img = Image.open(filename)
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            self.image_preview.config(image=photo)
            self.image_preview.image = photo
    
    def add_files(self):
        filetypes = [("PDF Files", "*.pdf")]
        files = filedialog.askopenfilenames(title="Select PDF Files", filetypes=filetypes)
        if files:
            self.files.extend(files)
            self.update_listbox()
            self.status_var.set(f"{len(self.files)} file(s) selected")
            
            if len(self.files) == 1:
                self.update_page_count(self.files[0])
    
    def update_page_count(self, pdf_path):
        try:
            with open(pdf_path, "rb") as f:
                reader = PdfReader(f)
                page_count = len(reader.pages)
                self.start_page.set(1)
                self.end_page.set(page_count)
                self.start_spin.config(to=page_count)
                self.end_spin.config(to=page_count)
        except Exception as e:
            print(f"Error reading PDF page count: {e}")
    
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
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
    
    def update_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def start_watermark(self):
        if not self.files:
            messagebox.showwarning("Warning", "No PDF files selected!")
            return
            
        output_folder = self.output_entry.get()
        if not output_folder:
            messagebox.showwarning("Warning", "Please select an output folder!")
            return
            
        if self.watermark_type.get() == "text" and not self.text_entry.get():
            messagebox.showwarning("Warning", "Please enter watermark text!")
            return
            
        if self.watermark_type.get() == "image" and not self.selected_image:
            messagebox.showwarning("Warning", "Please select a watermark image!")
            return
            
        if self.start_page.get() > self.end_page.get():
            messagebox.showwarning("Warning", "Start page cannot be greater than end page!")
            return
            
        thread = threading.Thread(
            target=self.apply_watermark,
            args=(output_folder,),
            daemon=True
        )
        thread.start()
    
    def apply_watermark(self, output_folder):
        self.status_var.set("Starting watermarking...")
        
        try:
            os.makedirs(output_folder, exist_ok=True)
            success_count = 0
            
            for i, input_file in enumerate(self.files):
                try:
                    self.status_var.set(f"Processing {i+1}/{len(self.files)}: {os.path.basename(input_file)}")
                    
                    output_path = os.path.join(output_folder, f"watermarked_{Path(input_file).stem}.pdf")
                    
                    if self.watermark_type.get() == "text":
                        watermark_pdf = self.create_text_watermark()
                    else:
                        watermark_pdf = self.create_image_watermark()
                    
                    self.apply_to_pdf(input_file, output_path, watermark_pdf)
                    db.log_task(self.username, "Watermark-PDF", input_file, output_path)
                    
                    success_count += 1
                except Exception as e:
                    print(f"Error processing {input_file}: {str(e)}")
                    continue
            
            self.status_var.set(f"Watermarking complete! {success_count}/{len(self.files)} files processed")
            messagebox.showinfo("Success", f"Watermarked {success_count} file(s)")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Watermarking failed:\n{str(e)}")
    
    def get_position_coordinates(self, width, height, obj_width, obj_height):
        margin = 50
        pos = self.watermark_position.get()
        
        if pos == "top-left":
            return (margin, height - margin - obj_height)
        elif pos == "top-center":
            return ((width - obj_width) / 2, height - margin - obj_height)
        elif pos == "top-right":
            return (width - margin - obj_width, height - margin - obj_height)
        elif pos == "center-left":
            return (margin, (height - obj_height) / 2)
        elif pos == "center":
            return ((width - obj_width) / 2, (height - obj_height) / 2)
        elif pos == "center-right":
            return (width - margin - obj_width, (height - obj_height) / 2)
        elif pos == "bottom-left":
            return (margin, margin)
        elif pos == "bottom-center":
            return ((width - obj_width) / 2, margin)
        elif pos == "bottom-right":
            return (width - margin - obj_width, margin)
        else:
            return ((width - obj_width) / 2, (height - obj_height) / 2)
    
    def create_text_watermark(self):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        alpha = 1 - (self.transparency.get() / 100)
        can.setFillColorRGB(*[c/255 for c in self.watermark_color], alpha=alpha)
        
        base_font = self.font_family.get()
        if "-" not in base_font:
            if self.bold_style.get() and self.italic_style.get():
                base_font += "-BoldOblique"
            elif self.bold_style.get():
                base_font += "-Bold"
            elif self.italic_style.get():
                base_font += "-Oblique"
        
        can.setFont(base_font, self.font_size.get())
        
        text = self.text_entry.get()
        text_width = can.stringWidth(text, base_font, self.font_size.get())
        text_height = self.font_size.get()
        
        width, height = letter
        x, y = self.get_position_coordinates(width, height, text_width, text_height)
        
        can.saveState()
        can.translate(x + text_width/2, y + text_height/2)
        can.rotate(self.rotation.get())
        can.translate(-(x + text_width/2), -(y + text_height/2))
        
        text_obj = can.beginText(x, y + text_height)
        if self.underline_style.get():
            text_obj.setUnderline(1)
        text_obj.textLine(text)
        can.drawText(text_obj)
        can.restoreState()
        
        can.save()
        packet.seek(0)
        return packet
    
    def create_image_watermark(self):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        img = Image.open(self.selected_image)
        img_width, img_height = img.size
        pdf_width, pdf_height = letter
        
        scale = self.image_scale.get() / 100.0
        
        if self.image_aspect.get():
            scaled_width = img_width * scale
            scaled_height = img_height * scale
        else:
            scaled_width = img_width * scale
            scaled_height = img_height * scale
        
        x, y = self.get_position_coordinates(pdf_width, pdf_height, scaled_width, scaled_height)
        
        alpha = 1 - (self.transparency.get() / 100)
        can.setFillAlpha(alpha)
        
        can.saveState()
        can.translate(x + scaled_width/2, y + scaled_height/2)
        can.rotate(self.rotation.get())
        can.translate(-(x + scaled_width/2), -(y + scaled_height/2))
        can.drawImage(ImageReader(img), x, y, width=scaled_width, height=scaled_height, mask='auto')
        can.restoreState()
        
        can.save()
        packet.seek(0)
        return packet
    
    def apply_to_pdf(self, input_path, output_path, watermark_pdf):
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        watermark_reader = PdfReader(watermark_pdf)
        watermark_page = watermark_reader.pages[0]
        
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            
            if (i+1) >= self.start_page.get() and (i+1) <= self.end_page.get():
                if self.layer_position.get() == "under":
                    new_page = PdfWriter().add_blank_page(
                        width=float(page.mediabox[2]),
                        height=float(page.mediabox[3])
                    )
                    new_page.merge_page(watermark_page)
                    new_page.merge_page(page)
                    writer.add_page(new_page)
                else:
                    page.merge_page(watermark_page)
                    writer.add_page(page)
            else:
                writer.add_page(page)
        
        with open(output_path, "wb") as f:
            writer.write(f)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDF Watermark Tool")
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    
    PDFWatermarkTab(notebook)
    root.mainloop()