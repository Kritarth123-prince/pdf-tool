import os
import fitz
import tkinter as tk
from PIL import ImageTk, Image
from db_connector import DBConnector
from tkinter import filedialog, messagebox, ttk

db = DBConnector()

class PDFSplitterTab:
    def __init__(self, notebook, username):
        self.username = username
        self.pdf_file = None
        self.pages = []
        self.preview_images = []
        self.selected_pages = []
        self.original_pdf_filename = None

        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text='Split PDF')

        button_frame = tk.Frame(self.tab)
        button_frame.pack(pady=10, fill='x')

        tk.Button(button_frame, text="Select PDF", command=self.select_pdf,
                  bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Split Pages", command=self.split_pages,
                  bg="#FF9800", fg="white", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

        self.page_label = tk.Label(self.tab, text="No PDF loaded", font=("Helvetica", 10))
        self.page_label.pack()

        preview_container = tk.Frame(self.tab)
        preview_container.pack(expand=True, fill='both')

        self.canvas = tk.Canvas(preview_container)
        self.scrollbar = tk.Scrollbar(preview_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return

        self.pdf_file = file_path
        self.original_pdf_filename = os.path.splitext(os.path.basename(self.pdf_file))[0]
        self.page_label.config(text="Loading pages...")

        try:
            doc = fitz.open(self.pdf_file)
            self.pages = []

            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                self.pages.append(img)

            self.page_label.config(text=f"Loaded {len(self.pages)} pages")
            self.display_previews()
            self.show_additional_controls()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")

    def display_previews(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.preview_images = []
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        images_per_row = max(1, width // 150)
        row_height = 200
        max_rows = max(1, height // row_height)

        for i, page in enumerate(self.pages):
            thumb = page.copy()
            thumb.thumbnail((150, 200))
            img = ImageTk.PhotoImage(thumb)
            self.preview_images.append(img)

            row = i // images_per_row
            col = i % images_per_row

            frame = tk.Frame(self.scroll_frame, borderwidth=1, relief='solid', padx=5, pady=5)
            frame.grid(row=row, column=col, padx=5, pady=5)

            label = tk.Label(frame, image=img)
            label.pack()

            checkbox_var = tk.IntVar()
            checkbox = tk.Checkbutton(frame, text=f"Page {i + 1}", variable=checkbox_var,
                                      command=lambda i=i, var=checkbox_var: self.toggle_page(i, var))
            checkbox.pack()

    def toggle_page(self, index, var):
        if var.get() == 1:
            if index not in self.selected_pages:
                self.selected_pages.append(index)
        else:
            if index in self.selected_pages:
                self.selected_pages.remove(index)

    def show_additional_controls(self):
        options_frame = tk.Frame(self.tab)
        options_frame.pack(fill="x", pady=5)

        self.file_type_label = tk.Label(options_frame, text="Select image format (PNG, JPG, JPEG):", font=("Helvetica", 10))
        self.file_type_label.pack(side=tk.LEFT, padx=5)

        self.file_type_combo = ttk.Combobox(options_frame, values=["PNG", "JPG", "JPEG"], state="normal")
        self.file_type_combo.set("PNG")
        self.file_type_combo.pack(side=tk.LEFT, padx=5)

        self.select_all_var = tk.IntVar()
        self.select_all_checkbox = tk.Checkbutton(options_frame, text="Select All Pages", variable=self.select_all_var,
                                                  command=self.select_all_pages)
        self.select_all_checkbox.pack(side=tk.RIGHT, padx=5)

    def select_all_pages(self):
        if self.select_all_var.get() == 1:
            self.selected_pages = list(range(len(self.pages)))
        else:
            self.selected_pages = []
        self.update_page_checkboxes()

    def update_page_checkboxes(self):
        for widget in self.scroll_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Checkbutton):
                        child.deselect() if self.select_all_var.get() == 0 else child.select()

    def split_pages(self):
        if not self.pdf_file or not self.pages:
            messagebox.showerror("Error", "No PDF loaded.")
            return

        if not self.selected_pages:
            messagebox.showerror("Error", "No pages selected for splitting.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if not output_dir:
            return

        file_type = self.file_type_combo.get().strip().lower()

        try:
            for i in self.selected_pages:
                output_file = os.path.join(output_dir, f"{self.original_pdf_filename}_page_{i + 1}.{file_type}")
                image_to_save = self.pages[i]
                if file_type in ['jpg', 'jpeg']:
                    image_to_save = image_to_save.convert('RGB')
                image_to_save.save(output_file, file_type.upper())

                db.log_task(self.username, "Split-PDF", self.pdf_file, output_file)

            messagebox.showinfo("Success", f"Saved {len(self.selected_pages)} selected pages as {file_type.upper()} images.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save images: {str(e)}")
