# 📄 Advanced PDF Tool

A desktop GUI-based Python application for managing, editing, and converting PDF, image, and Office files. The app includes user login/registration, file conversion utilities, and task logging with a MySQL database backend.

---

## 🧰 Features

- 🔐 **User Login & Registration**
- 🖼️ **Image to PDF** Conversion
- ✂️ **Image Resizer & Enhancer**
- 📐 **PDF Resize & Optimize**
- 🧩 **Merge Multiple PDFs**
- ✂️ **Split PDFs**
- 💧 **Add Watermark to PDF**
- 🛡️ **Encrypt/Decrypt PDF**
- 🔄 **PDF ↔ Word** Conversion
- 📊 **PDF ↔ PowerPoint**
- 📈 **PDF ↔ Excel**
- 🗂️ **Activity Logging with MySQL**

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Kritarth123-prince/pdf-tool.git
cd pdf-tool
```

### 2. Set Up the Virtual Environment

It is recommended to create a virtual environment in the root directory of your project to keep your project dependencies isolated from your global Python environment.

**For macOS/Linux:**

``` bash
python3 -m venv venv
source venv/bin/activate
```

**For Windows:**

``` bash
python -m venv venv
venv\Scripts\activate
```

Once activated, you should see (venv) at the beginning of your terminal prompt, indicating that the virtual environment is active.

### 3. Install the Required Dependencies

Now that the virtual environment is active, install all the dependencies specified in the requirements.txt file.

```bash
pip install -r requirements.txt
```

This will install the necessary libraries for the project within your virtual environment.

### 4. Set Up Environment Variables

Create a .env file in the root directory of the project and configure the following environment variables with your own MySQL credentials:

```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=pdf_tool
```

> **Note:** Replace `yourpassword` with your MySQL password. The `.env` file is used to store sensitive information and should **never** be committed to Git.

```bash
pdf-tool/
├── main_login.py         # Main entry point to start the login window
├── db_connector.py       # Manages database connection and queries
├── image_to_pdf.py       # Image to PDF conversion logic
├── img_enhance.py        # Image resizing and enhancement
├── pdf_merger.py         # PDF merging functionality
├── pdf_splitter.py       # PDF splitting functionality
├── pdf_enhance.py        # PDF resize and optimization
├── pdf_watermark.py      # Watermarking PDFs
├── encrypt_decrypt.py    # PDF encryption and decryption
├── pdf_word.py           # PDF to Word conversion logic
├── pdf_ppt.py            # PDF to PowerPoint conversion logic
├── excel_pdf.py          # PDF to Excel and vice versa conversion
├── requirements.txt      # Lists required Python packages
├── .gitignore            # Git ignore file for excluding unwanted files
└── .env                  # Example .env file (configure your database settings)
```
