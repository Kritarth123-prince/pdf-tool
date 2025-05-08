import os
import tkinter as tk
from pathlib import Path
from pdf2docx import Converter
from db_connector import DBConnector
from docx2pdf import convert as docx_to_pdf
from tkinter import filedialog, messagebox, ttk

db = DBConnector()

class PDFWordTab:
    def __init__(self, notebook, username):
        self.username = username
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="PDF ↔ Word")

        button_frame = ttk.Frame(self.tab)
        button_frame.pack(pady=20)

        pdf_to_word_frame = ttk.LabelFrame(button_frame, text="PDF to Word Conversion")
        pdf_to_word_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tk.Button(pdf_to_word_frame, text="Select PDF(s)", command=self.select_pdfs,
                  width=20, bg="#4285F4", fg="white").pack(pady=5)
        
        self.multi_pdf_var = tk.IntVar(value=1)
        tk.Checkbutton(pdf_to_word_frame, text="Convert multiple files", 
                       variable=self.multi_pdf_var, bg="white").pack(pady=5)
        
        tk.Button(pdf_to_word_frame, text="Convert to Word", command=self.pdf_to_word,
                  width=20, bg="#EA4335", fg="white").pack(pady=5)

        word_to_pdf_frame = ttk.LabelFrame(button_frame, text="Word to PDF Conversion")
        word_to_pdf_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        tk.Button(word_to_pdf_frame, text="Select Word File(s)", command=self.select_word_files,
                  width=20, bg="#34A853", fg="white").pack(pady=5)
        
        self.multi_word_var = tk.IntVar(value=1)
        tk.Checkbutton(word_to_pdf_frame, text="Convert multiple files", 
                        variable=self.multi_word_var, bg="white").pack(pady=5)
        
        tk.Button(word_to_pdf_frame, text="Convert to PDF", command=self.word_to_pdf,
                  width=20, bg="#EA4335", fg="white").pack(pady=5)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(self.tab, textvariable=self.status_var, relief=tk.SUNKEN,
                 anchor=tk.W).pack(fill=tk.X, pady=(0, 10), padx=10)

        self.selected_pdfs = []
        self.selected_word_files = []

    def select_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Select PDF File(s)",
            filetypes=[("PDF files", "*.pdf")]
        )
        if files:
            self.selected_pdfs = list(files)
            count = len(self.selected_pdfs)
            self.status_var.set(f"Selected {count} PDF file(s)")

    def select_word_files(self):
        files = filedialog.askopenfilenames(
            title="Select Word File(s)",
            filetypes=[("Word files", "*.docx")]
        )
        if files:
            self.selected_word_files = list(files)
            count = len(self.selected_word_files)
            self.status_var.set(f"Selected {count} Word file(s)")

    def pdf_to_word(self):
        if not self.selected_pdfs:
            messagebox.showwarning("Warning", "No PDF files selected!")
            return

        convert_multiple = self.multi_pdf_var.get()
        
        if convert_multiple:
            output_dir = filedialog.askdirectory(title="Select Output Folder")
            if not output_dir:
                return
            
            success_count = 0
            for pdf_path in self.selected_pdfs:
                try:
                    output_path = os.path.join(output_dir, 
                                            f"{Path(pdf_path).stem}.docx")
                    self._convert_with_pdf2docx(pdf_path, output_path)
                    success_count += 1
                    db.log_task(self.username, 'pdf_to_word', pdf_path, output_path)
                except Exception as e:
                    self.status_var.set(f"Error converting {Path(pdf_path).name}: {str(e)}")
                    continue
            
            self.status_var.set(f"Successfully converted {success_count}/{len(self.selected_pdfs)} files")
            if success_count > 0:
                messagebox.showinfo("Success", 
                                  f"Converted {success_count} PDF(s) to Word\nin folder: {output_dir}")
        else:
            pdf_path = self.selected_pdfs[0]
            output_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx")],
                title="Save as Word",
                initialfile=f"{Path(pdf_path).stem}.docx"
            )
            if not output_path:
                return
            
            try:
                self._convert_with_pdf2docx(pdf_path, output_path)
                messagebox.showinfo("Success", 
                                  f"PDF successfully converted to Word.\nSaved as:\n{output_path}")
                db.log_task(self.username, 'pdf_to_word', pdf_path, output_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert PDF to Word:\n{e}")

    def _convert_with_pdf2docx(self, pdf_path, docx_path):
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

    def word_to_pdf(self):
        if not self.selected_word_files:
            messagebox.showwarning("Warning", "No Word files selected!")
            return

        convert_multiple = self.multi_word_var.get()
        
        if convert_multiple:
            output_dir = filedialog.askdirectory(title="Select Output Folder")
            if not output_dir:
                return
            
            success_count = 0
            for word_path in self.selected_word_files:
                try:
                    output_path = os.path.join(output_dir, 
                                             f"{Path(word_path).stem}.pdf")
                    docx_to_pdf(word_path, output_path)
                    success_count += 1
                    db.log_task(self.username, 'word_to_pdf', word_path, output_path)
                except Exception as e:
                    self.status_var.set(f"Error converting {Path(word_path).name}: {str(e)}")
                    continue
            
            self.status_var.set(f"Successfully converted {success_count}/{len(self.selected_word_files)} files")
            if success_count > 0:
                messagebox.showinfo("Success", 
                                  f"Converted {success_count} Word file(s) to PDF\nin folder: {output_dir}")
        else:
            word_path = self.selected_word_files[0]
            output_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save as PDF",
                initialfile=f"{Path(word_path).stem}.pdf"
            )
            if not output_path:
                return
            
            try:
                docx_to_pdf(word_path, output_path)
                messagebox.showinfo("Success", 
                                  f"Word file successfully converted to PDF.\nSaved as:\n{output_path}")
                db.log_task(self.username, 'word_to_pdf', word_path, output_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert Word to PDF:\n{e}")
