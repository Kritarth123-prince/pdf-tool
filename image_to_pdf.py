import os
import tkinter as tk
from fpdf import FPDF
from PIL import Image
from tkinter import ttk
from PIL import Image, ImageTk
from db_connector import DBConnector
from tkinter import filedialog, messagebox

db = DBConnector()

class ImageToPDFTab:
    def __init__(self, notebook, username):
        self.username = username
        self.image_files = []
        self.output_pdf = "output.pdf"
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text='Image to PDF')
        
        self.drag_start_pos = None
        self.dragged_item = None
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill='y', padx=(0, 10))

        button_frame = tk.Frame(left_panel)
        button_frame.pack(pady=(0, 10), fill='x')

        tk.Button(button_frame, text="Add Images", command=self.add_images, bg="#4285F4", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_selected, bg="#EA4335", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Move Up", command=self.move_up, bg="#FBBC05", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Move Down", command=self.move_down, bg="#FBBC05", fg="white").pack(side=tk.LEFT, padx=2)

        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill='both', expand=True)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)

        output_frame = tk.Frame(left_panel)
        output_frame.pack(fill='x', pady=(10, 0))

        ttk.Label(output_frame, text="Output PDF:").pack(side=tk.LEFT)
        self.output_entry = ttk.Entry(output_frame, width=30)
        self.output_entry.pack(side=tk.LEFT, padx=5, expand=True, fill='x')
        self.output_entry.insert(0, self.output_pdf)

        tk.Button(output_frame, text="Browse", command=self.browse_output, bg="#34A853", fg="white").pack(side=tk.LEFT)

        tk.Button(left_panel, text="Convert to PDF", command=self.convert_to_pdf, 
                 bg="#673AB7", fg="white").pack(pady=(10, 0), fill='x')

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill='both', expand=True)

        self.preview_label = ttk.Label(right_panel, text="Image Preview", font=('Helvetica', 10, 'bold'))
        self.preview_label.pack(pady=(0, 5))

        self.canvas = tk.Canvas(right_panel)
        self.scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.status_label = ttk.Label(self.tab, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(fill='x', padx=10, pady=(0, 10))

        self.preview_images = []
        self.image_labels = []
        self.selected_preview = None

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def add_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if files:
            self.image_files.extend(files)
            self.update_listbox()
            self.update_preview_grid()
            self.status_label.config(text=f"{len(self.image_files)} images loaded")

    def remove_selected(self):
        selected = self.listbox.curselection()
        if selected:
            del self.image_files[selected[0]]
            self.update_listbox()
            self.update_preview_grid()

    def move_up(self):
        selected = self.listbox.curselection()
        if selected and selected[0] > 0:
            i = selected[0]
            self.image_files[i], self.image_files[i-1] = self.image_files[i-1], self.image_files[i]
            self.update_listbox()
            self.listbox.select_set(i-1)
            self.update_preview_grid()

    def move_down(self):
        selected = self.listbox.curselection()
        if selected and selected[0] < len(self.image_files) - 1:
            i = selected[0]
            self.image_files[i], self.image_files[i+1] = self.image_files[i+1], self.image_files[i]
            self.update_listbox()
            self.listbox.select_set(i+1)
            self.update_preview_grid()

    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filename:
            self.output_pdf = filename
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_pdf)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for file in self.image_files:
            self.listbox.insert(tk.END, os.path.basename(file))

    def update_preview_grid(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.preview_images = []
        self.image_labels = []
        
        if not self.image_files:
            return
        
        columns = 3
        for i, image_file in enumerate(self.image_files):
            row = i // columns
            col = i % columns
            
            try:
                img = Image.open(image_file)
                img.thumbnail((150, 150))
                
                photo = ImageTk.PhotoImage(img)
                self.preview_images.append(photo)
                
                label = ttk.Label(self.scrollable_frame, image=photo)
                label.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
                label.image_file = image_file
                label.index = i
                
                filename_label = ttk.Label(self.scrollable_frame, text=os.path.basename(image_file), 
                                         wraplength=150)
                filename_label.grid(row=row+1, column=col, padx=5, pady=(0, 10))
                
                label.bind("<ButtonPress-1>", self.on_drag_start)
                label.bind("<B1-Motion>", self.on_drag_motion)
                label.bind("<ButtonRelease-1>", self.on_drag_release)
                
                self.image_labels.append(label)
                
            except Exception as e:
                print(f"Error loading image {image_file}: {e}")
        
        for i in range(columns):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)

    def on_drag_start(self, event):
        widget = event.widget
        self.drag_start_pos = (event.x, event.y)
        self.dragged_item = widget
        widget.lift()

    def on_drag_motion(self, event):
        widget = self.dragged_item
        if widget:
            x = widget.winfo_x() - self.drag_start_pos[0] + event.x
            y = widget.winfo_y() - self.drag_start_pos[1] + event.y
            widget.place(x=x, y=y)

    def on_drag_release(self, event):
        if not self.dragged_item:
            return
            
        widget = self.dragged_item
        target = None
        
        for label in self.image_labels:
            if (label.winfo_rootx() <= event.x_root <= label.winfo_rootx() + label.winfo_width() and
                label.winfo_rooty() <= event.y_root <= label.winfo_rooty() + label.winfo_height()):
                target = label
                break
        
        if target and target != widget:
            i, j = widget.index, target.index
            self.image_files[i], self.image_files[j] = self.image_files[j], self.image_files[i]
            
            self.update_listbox()
            self.update_preview_grid()
            
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(j if i == widget.index else i)
        
        self.drag_start_pos = None
        self.dragged_item = None

    def convert_to_pdf(self):
        if not self.image_files:
            messagebox.showerror("Error", "No images selected!")
            return

        output_path = self.output_entry.get()
        if not output_path:
            messagebox.showerror("Error", "Please specify output PDF name")
            return

        try:
            pdf = FPDF()
            for i, image_file in enumerate(self.image_files):
                img = Image.open(image_file)
                img = img.convert('RGB')
                width, height = img.size
                orientation = 'P' if height > width else 'L'
                pdf.add_page(orientation=orientation)
                
                pdf_width = pdf.w - 20
                pdf_height = (height * pdf_width) / width
                
                if pdf_height > pdf.h - 20:
                    pdf_height = pdf.h - 20
                    pdf_width = (width * pdf_height) / height
                
                x = (pdf.w - pdf_width) / 2
                y = (pdf.h - pdf_height) / 2
                
                temp_img = f"temp_{i}.jpg"
                img.save(temp_img)
                pdf.image(temp_img, x=x, y=y, w=pdf_width)
                os.remove(temp_img)
                
            pdf.output(output_path)
            self.status_label.config(text=f"PDF saved: {output_path}")
            messagebox.showinfo("Success", f"PDF created at:\n{output_path}")
            db.log_task(self.username, "image_to_pdf", self.image_files, output_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))