import tkinter as tk
from tkinter import ttk
from pdf_word import PDFWordTab
from tkinter import messagebox
from pdf_merger import MergePDFTab
from pdf_enhance import PDFSizeTab
from db_connector import DBConnector
from image_to_pdf import ImageToPDFTab
from excel_pdf import ExcelConverterTab
from img_enhance import ImageResizerTab
from pdf_splitter import PDFSplitterTab
from pdf_watermark import PDFWatermarkTab
from pdf_ppt import PowerPointConverterTab
from encrypt_decrypt import PDFSecurityTab

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("Login")
        self.root.geometry("300x250")

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Login", command=self.validate_login, bg="blue", fg="white").pack(pady=10)
        tk.Button(root, text="Register", command=self.show_register_window, bg="green", fg="white").pack()

    def validate_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        db = DBConnector()
        result = db.execute_query("SELECT * FROM users WHERE username = %s AND password = %s", (username, password), fetch_one=True)

        if result:
            self.root.destroy()
            self.on_success(username)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def show_register_window(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("300x220")

        tk.Label(register_window, text="New Username").pack(pady=5)
        username_entry = tk.Entry(register_window, bg="#f0f0ff")
        username_entry.pack()

        tk.Label(register_window, text="New Password").pack(pady=5)
        password_entry = tk.Entry(register_window, show="*", bg="#f0fff0")
        password_entry.pack()

        def register_user():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                messagebox.showerror("Error", "All fields are required", parent=register_window)
                return

            db = DBConnector()
            existing = db.execute_query("SELECT * FROM users WHERE username = %s", (username,), fetch_one=True)
            if existing:
                messagebox.showerror("Error", "Username already exists", parent=register_window)
                return

            db.execute_query("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            messagebox.showinfo("Success", "User registered successfully!", parent=register_window)
            register_window.destroy()

        tk.Button(register_window, text="Register", command=register_user, bg="purple", fg="white").pack(pady=20)

class PDFToolApp:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title(f"Advanced PDF Tools - {self.username.capitalize()}")
        self.root.geometry("900x700")

        self.configure_styles()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        ImageToPDFTab(self.notebook, self.username)
        ImageResizerTab(self.notebook, self.username)
        PDFSizeTab(self.notebook, self.username)
        MergePDFTab(self.notebook, self.username)
        PDFSplitterTab(self.notebook, self.username)
        PDFWatermarkTab(self.notebook, self.username)
        PDFSecurityTab(self.notebook, self.username)
        PDFWordTab(self.notebook, self.username)
        PowerPointConverterTab(self.notebook, self.username)
        ExcelConverterTab(self.notebook, self.username)

    def configure_styles(self):
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Helvetica', 10, 'bold'))
        style.configure('TButton', font=('Helvetica', 9), padding=5)

    def run(self):
        self.root.mainloop()

def launch_app(username):
    app = PDFToolApp(username)
    app.run()

if __name__ == "__main__":
    print("Initializing... Please wait.")
    root = tk.Tk()
    LoginWindow(root, launch_app)
    root.mainloop()
