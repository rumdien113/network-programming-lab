import tkinter as tk
from tkinter import messagebox
import hashlib
import requests

class ClientSignUp:
    SERVER_URL = "http://192.168.232.111:5000"

    def __init__(self, root):
        self.root = root
        self.root.title("Đăng ký (Client)")
        self.root.geometry("600x350")

        self.lbl_title = tk.Label(root, text="MAIL APPLICATION", fg="red", font=("Tahoma", 15, "bold"))
        self.lbl_title.pack(pady=(10, 0))

        self.lbl_heading = tk.Label(root, text="Đăng ký", font=("Tahoma", 13))
        self.lbl_heading.pack()

        self.lbl_email = tk.Label(root, text="Email")
        self.lbl_email.pack()
        self.tf_email = tk.Entry(root, width=40, font=("Tahoma", 12))
        self.tf_email.pack(pady=(0, 10))

        self.lbl_password = tk.Label(root, text="Mật khẩu")
        self.lbl_password.pack()
        self.tf_password = tk.Entry(root, show='*', width=40, font=("Tahoma", 12))
        self.tf_password.pack(pady=(0, 10))

        self.btn_sign_up = tk.Button(root, text="ĐĂNG KÝ", bg="red", fg="white", command=self.sign_up)
        self.btn_sign_up.pack(pady=(10, 0))

    def sign_up(self):
        email = self.tf_email.get()
        password = self.tf_password.get()

        if email and password:
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            try:
                response = requests.post(f"{self.SERVER_URL}/create_account", json={"email": email, "password": hashed_password})
                data = response.json()

                if data["status"] == "SUCCESS":
                    messagebox.showinfo("Notification", data["message"])
                    self.root.destroy()
                else:
                    messagebox.showwarning("Notification", data["message"])
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            if not email:
                messagebox.showerror("Error", "Email cannot be empty.")
            if not password:
                messagebox.showerror("Error", "Password cannot be empty.")