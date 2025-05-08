import os
import tkinter as tk
from PyPDF2 import PdfMerger
from db_connector import DBConnector
from tkinter import filedialog, messagebox

db = DBConnector()

class MergePDFTab:
    def __init__(self, notebook, username):
        self.username = username
        self.pdf_files = []
        self.default_output = "merged_output.pdf"

        self.tab = tk.Frame(notebook)
        notebook.add(self.tab, text="Merge PDFs")
        self.create_widgets()

    def create_widgets(self):
        button_frame = tk.Frame(self.tab)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add PDFs", command=self.add_pdfs, bg='green', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_selected, bg='red', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Move Up", command=self.move_up).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Move Down", command=self.move_down).pack(side=tk.LEFT, padx=5)

        list_frame = tk.Frame(self.tab)
        list_frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)

        output_frame = tk.Frame(self.tab)
        output_frame.pack(pady=5, fill='x', padx=10)

        tk.Label(output_frame, text="Output PDF:").pack(side=tk.LEFT)
        self.output_entry = tk.Entry(output_frame, width=50)
        self.output_entry.pack(side=tk.LEFT, padx=5)
        self.output_entry.insert(0, self.default_output)

        tk.Button(output_frame, text="Browse", command=self.browse_output, bg="#9C27B0", fg="white").pack(side=tk.LEFT)

        tk.Button(self.tab, text="Merge and Save", command=self.merge_pdfs, bg='orange', fg='white').pack(pady=10)

        self.status = tk.Label(self.tab, text="Ready")
        self.status.pack()

    def add_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            self.pdf_files.extend(files)
            self.update_listbox()
            self.status.config(text=f"{len(self.pdf_files)} files selected")

    def remove_selected(self):
        selected = self.listbox.curselection()
        if selected:
            del self.pdf_files[selected[0]]
            self.update_listbox()

    def move_up(self):
        selected = self.listbox.curselection()
        if selected and selected[0] > 0:
            i = selected[0]
            self.pdf_files[i], self.pdf_files[i - 1] = self.pdf_files[i - 1], self.pdf_files[i]
            self.update_listbox()
            self.listbox.select_set(i - 1)

    def move_down(self):
        selected = self.listbox.curselection()
        if selected and selected[0] < len(self.pdf_files) - 1:
            i = selected[0]
            self.pdf_files[i], self.pdf_files[i + 1] = self.pdf_files[i + 1], self.pdf_files[i]
            self.update_listbox()
            self.listbox.select_set(i + 1)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for file in self.pdf_files:
            self.listbox.insert(tk.END, os.path.basename(file))

    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    def merge_pdfs(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDFs selected!")
            return

        output = self.output_entry.get().strip()
        if not output:
            messagebox.showerror("Error", "Please enter an output filename!")
            return

        try:
            merger = PdfMerger()
            for pdf in self.pdf_files:
                merger.append(pdf)
            merger.write(output)
            merger.close()
            self.status.config(text=f"Merged PDF saved: {output}")
            messagebox.showinfo("Success", f"PDF saved to:\n{output}")
            
            db.log_task(self.username, "merge", self.pdf_files, output)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Merging failed")