import tkinter as tk
from tkinter import messagebox, filedialog
import struct
import os
import subprocess

MARKER = b'SECRET_START_2025'

def sign_file(filepath):
    # Пример вызова signtool для подписи файла
    # Нужно заменить путь к cert.pfx и пароль на актуальные
    cert_path = "D:\6semester\info_seq\lab2\mycert.pfx"
    password = "12345678"
    
    signtool_path = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
    if not os.path.exists(signtool_path):
        messagebox.showwarning("SignTool", "signtool.exe не найден, подпись не выполнена.")
        return False

    cmd = [
        signtool_path,
        "sign",
        "/f", cert_path,
        "/p", password,
        "/fd", "SHA256",
        "/tr", "http://timestamp.digicert.com",
        "/td", "SHA256",
        "-v", filepath
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            messagebox.showwarning("SignTool", f"Ошибка подписи:\n{result.stderr}")
            return False
        return True
    except Exception as e:
        messagebox.showwarning("SignTool", f"Ошибка вызова signtool:\n{e}")
        return False

def create_app_with_secret(secret_text):
    if len(secret_text) > 10000:
        messagebox.showerror("Ошибка", "Секрет не должен превышать 10 000 символов")
        return

    # Выбираем шаблон exe
    template_path = filedialog.askopenfilename(title="Выберите шаблон lab2_2.exe", filetypes=[("Executable files", "*.exe")])
    if not template_path:
        return

    # Читаем шаблон
    with open(template_path, "rb") as f:
        data = f.read()

    secret_bytes = secret_text.encode("utf-8")
    secret_len = len(secret_bytes)

    # Формируем новую бинарную часть: MARKER + длина (4 байта little endian) + секрет
    secret_data = MARKER + struct.pack("<I", secret_len) + secret_bytes

    # Создаем новый файл — дописываем секрет в конец шаблона
    new_filename = filedialog.asksaveasfilename(title="Сохранить готовое приложение как", defaultextension=".exe", filetypes=[("Executable files", "*.exe")])
    if not new_filename:
        return

    with open(new_filename, "wb") as f:
        f.write(data)
        f.write(secret_data)

    # Подписываем файл
    if sign_file(new_filename):
        messagebox.showinfo("Успех", "Приложение создано и подписано успешно!")
    else:
        messagebox.showinfo("Внимание", "Приложение создано, но подпись не выполнена.")

def on_create_click():
    secret_text = text_input.get("1.0", tk.END).strip()
    if not secret_text:
        messagebox.showerror("Ошибка", "Введите секрет")
        return
    create_app_with_secret(secret_text)

root = tk.Tk()
root.title("Создатель приложения с секретом")
root.geometry("600x400")

label = tk.Label(root, text="Введите секрет (до 10 000 символов):")
label.pack(pady=5)

text_input = tk.Text(root, height=15, width=70)
text_input.pack(padx=10)

create_btn = tk.Button(root, text="Создать приложение с секретом", command=on_create_click)
create_btn.pack(pady=10)

root.mainloop()
