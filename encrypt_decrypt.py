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

class PDFSecurityTab:
    def __init__(self, notebook,username):
        self.username = username
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="PDF Security")
        
        self.files = []
        self.output_folder = tk.StringVar()
        self.mode = tk.StringVar(value="encrypt")
        
        self.encrypt_password = tk.StringVar()
        self.encrypt_confirm = tk.StringVar()
        self.use_permission = tk.BooleanVar(value=False)
        self.permission_password = tk.StringVar()
        self.permission_confirm = tk.StringVar()
        self.prevent_printing = tk.BooleanVar(value=False)
        self.prevent_copying = tk.BooleanVar(value=False)
        self.prevent_modifying = tk.BooleanVar(value=False)
        
        self.user_password = tk.StringVar()
        self.owner_password = tk.StringVar()
        self.remove_restrictions = tk.BooleanVar(value=True)
        
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        mode_frame = ttk.LabelFrame(main_frame, text="Security Mode")
        mode_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Encrypt PDF", 
                       variable=self.mode, 
                       value="encrypt",
                       command=self.toggle_mode).pack(side="left", padx=5)
        
        ttk.Radiobutton(mode_frame, text="Decrypt PDF", 
                       variable=self.mode, 
                       value="decrypt",
                       command=self.toggle_mode).pack(side="left", padx=5)
        
        self.encrypt_frame = ttk.Frame(main_frame)
        
        password_frame = ttk.LabelFrame(self.encrypt_frame, text="Encryption Settings")
        password_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(password_frame, text="Password to open document:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(password_frame, textvariable=self.encrypt_password, show="*").grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(password_frame, text="Re-enter password:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(password_frame, textvariable=self.encrypt_confirm, show="*").grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Checkbutton(password_frame, text="Set permissions password", variable=self.use_permission,
                       command=self.toggle_permission).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        self.perm_frame = ttk.Frame(password_frame)
        
        ttk.Label(self.perm_frame, text="Permissions password:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(self.perm_frame, textvariable=self.permission_password, show="*").grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.perm_frame, text="Re-enter password:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(self.perm_frame, textvariable=self.permission_confirm, show="*").grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        perm_options = ttk.LabelFrame(self.perm_frame, text="Permissions")
        perm_options.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Checkbutton(perm_options, text="Prevent Printing", variable=self.prevent_printing).pack(anchor="w", padx=5, pady=2)
        ttk.Checkbutton(perm_options, text="Prevent Copying", variable=self.prevent_copying).pack(anchor="w", padx=5, pady=2)
        ttk.Checkbutton(perm_options, text="Prevent Modifying", variable=self.prevent_modifying).pack(anchor="w", padx=5, pady=2)
        
        self.perm_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        self.perm_frame.grid_remove()
        
        self.decrypt_frame = ttk.Frame(main_frame)
        
        decrypt_password_frame = ttk.LabelFrame(self.decrypt_frame, text="Decryption Settings")
        decrypt_password_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(decrypt_password_frame, text="Document password (if any):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(decrypt_password_frame, textvariable=self.user_password, show="*").grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(decrypt_password_frame, text="Permissions password (if any):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(decrypt_password_frame, textvariable=self.owner_password, show="*").grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Checkbutton(decrypt_password_frame, text="Remove all restrictions", variable=self.remove_restrictions).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        file_frame = ttk.LabelFrame(main_frame, text="PDF Files")
        file_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(file_frame, command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(button_frame, text="Add PDFs", command=self.add_files, bg="#4285F4", fg="white", font=('Helvetica', 9, 'bold'), relief=tk.RAISED, borderwidth=2).pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_files, bg="#EA4335", fg="white", font=('Helvetica', 9, 'bold'), relief=tk.RAISED, borderwidth=2).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_files, bg="#FBBC05", fg="white", font=('Helvetica', 9, 'bold'), relief=tk.RAISED, borderwidth=2).pack(side="left", padx=5)
        
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(output_frame, text="Output Folder:").pack(side="left")
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_folder)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(output_frame, text="Browse", command=self.browse_output, bg="#34A853", fg="white", font=('Helvetica', 9, 'bold'), relief=tk.RAISED, borderwidth=2).pack(side="left")
        
        self.process_btn = tk.Button(main_frame, text="Encrypt PDFs", command=self.start_process, bg="#673AB7", fg="white", font=('Helvetica', 10, 'bold'), relief=tk.RAISED, borderwidth=2)
        self.process_btn.pack(pady=(10, 0), fill="x")
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.tab, textvariable=self.status_var, relief=tk.SUNKEN,
                 anchor=tk.W).pack(fill="x", padx=10, pady=(0, 10))
        
        self.toggle_mode()
    
    def toggle_mode(self):
        if self.mode.get() == "encrypt":
            self.encrypt_frame.pack(fill="x", pady=(10, 0))
            self.decrypt_frame.pack_forget()
            self.process_btn.config(text="Encrypt PDFs", bg="#673AB7")
        else:
            self.decrypt_frame.pack(fill="x", pady=(10, 0))
            self.encrypt_frame.pack_forget()
            self.process_btn.config(text="Decrypt PDFs", bg="#009688")

    def toggle_permission(self):
        if self.use_permission.get():
            self.perm_frame.grid()
        else:
            self.perm_frame.grid_remove()
    
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
    
    def validate_passwords(self):
        if not self.encrypt_password.get():
            messagebox.showwarning("Warning", "Please enter a password to open the document!")
            return False
            
        if self.encrypt_password.get() != self.encrypt_confirm.get():
            messagebox.showwarning("Warning", "Document passwords do not match!")
            return False
            
        if self.use_permission.get():
            if not self.permission_password.get():
                messagebox.showwarning("Warning", "Please enter a permissions password!")
                return False
                
            if self.permission_password.get() != self.permission_confirm.get():
                messagebox.showwarning("Warning", "Permissions passwords do not match!")
                return False
                
            if self.encrypt_password.get() == self.permission_password.get():
                messagebox.showwarning("Warning", "Document and permissions passwords cannot be the same!")
                return False
                
        return True
    
    def start_process(self):
        if not self.files:
            messagebox.showwarning("Warning", "No PDF files selected!")
            return
            
        if not self.output_folder.get():
            messagebox.showwarning("Warning", "Please select an output folder!")
            return
            
        if self.mode.get() == "encrypt" and not self.validate_passwords():
            return
            
        thread = threading.Thread(
            target=self.process_files,
            args=(self.output_folder.get(),),
            daemon=True
        )
        thread.start()
    
    def process_files(self, output_folder):
        self.status_var.set(f"Starting {self.mode.get()}ion...")
        
        try:
            os.makedirs(output_folder, exist_ok=True)
            success_count = 0
            
            for i, input_file in enumerate(self.files):
                try:
                    self.status_var.set(f"Processing {i+1}/{len(self.files)}: {os.path.basename(input_file)}")
                    
                    output_path = os.path.join(output_folder, f"{self.mode.get()}ed_{Path(input_file).stem}.pdf")
                    
                    if self.mode.get() == "encrypt":
                        self.encrypt_pdf(input_file, output_path)
                    else:
                        self.decrypt_pdf(input_file, output_path)

                    db.log_task(
                    username=self.username,
                    task_type="encrypt" if self.mode.get() == "encrypt" else "decrypt",
                    input_files=input_file,
                    output_file=output_path
                    )
                    
                    success_count += 1
                except Exception as e:
                    error_msg = f"Error processing {os.path.basename(input_file)}: {str(e)}"
                    print(error_msg)
                    self.status_var.set(error_msg)
                    continue
            
            self.status_var.set(f"{self.mode.get().title()}ion complete! {success_count}/{len(self.files)} files processed")
            messagebox.showinfo("Success", f"{self.mode.get().title()}ed {success_count} file(s)")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"{self.mode.get().title()}ion failed:\n{str(e)}")
    
    def encrypt_pdf(self, input_path, output_path):
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            writer.add_metadata(reader.metadata)
            
            if self.use_permission.get():
                permissions = 0
                if not self.prevent_printing.get():
                    permissions |= 0b000000000100
                if not self.prevent_copying.get():
                    permissions |= 0b000000100000
                if not self.prevent_modifying.get():
                    permissions |= 0b000000000010
                
                try:
                    writer.encrypt(
                        user_password=self.encrypt_password.get(),
                        owner_password=self.permission_password.get(),
                        use_128bit=True,
                        permissions=permissions
                    )
                except TypeError:
                    writer.encrypt(
                        user_pwd=self.encrypt_password.get(),
                        owner_pwd=self.permission_password.get(),
                        use_128bit=True
                    )
            else:
                try:
                    writer.encrypt(
                        user_password=self.encrypt_password.get(),
                        use_128bit=True
                    )
                except TypeError:
                    writer.encrypt(
                        user_pwd=self.encrypt_password.get(),
                        use_128bit=True
                    )
            
            with open(output_path, "wb") as f:
                writer.write(f)
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_pdf(self, input_path, output_path):
        try:
            reader = PdfReader(input_path)
            
            if reader.is_encrypted:
                passwords = []
                if self.user_password.get():
                    passwords.append(self.user_password.get())
                if self.owner_password.get():
                    passwords.append(self.owner_password.get())
                
                if not passwords:
                    passwords.append("")
                
                decrypted = False
                for password in passwords:
                    try:
                        if reader.decrypt(password):
                            decrypted = True
                            break
                    except Exception:
                        continue
                
                if not decrypted:
                    raise Exception("Failed to decrypt PDF - incorrect password(s)")
            
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            if hasattr(reader, 'metadata') and reader.metadata:
                writer.add_metadata(reader.metadata)
            
            if self.remove_restrictions.get():
                try:
                    if hasattr(writer, '_encrypt'):
                        writer._encrypt = None
                    if hasattr(writer, '_encryption_obj'):
                        writer._encryption_obj = None
                    
                    if hasattr(writer, '_root_object'):
                        if writer._root_object is not None:
                            if '/Encrypt' in writer._root_object:
                                del writer._root_object['/Encrypt']
                except Exception as e:
                    print(f"Warning: Could not fully remove restrictions: {e}")
            
            with open(output_path, "wb") as f:
                writer.write(f)
                
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")