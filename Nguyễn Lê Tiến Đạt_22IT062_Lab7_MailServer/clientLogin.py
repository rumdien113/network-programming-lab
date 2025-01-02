import tkinter as tk
from tkinter import messagebox
import hashlib
import requests
from clientSignUp import ClientSignUp
from clientHome import ClientHome


class ClientLogin(tk.Tk):
    SERVER_URL = "http://192.168.232.111:5000"

    def __init__(self):
        super().__init__()
        self.title("Đăng nhập (Client)")
        self.geometry("600x350")

        self.lbl_title = tk.Label(self, text="MAIL APPLICATION", fg="red", font=("Tahoma", 15, "bold"))
        self.lbl_title.pack(pady=(10, 0))

        self.lbl_heading = tk.Label(self, text="Đăng nhập", font=("Tahoma", 13))
        self.lbl_heading.pack()

        self.lbl_email = tk.Label(self, text="Email")
        self.lbl_email.pack()
        self.tf_email = tk.Entry(self, width=40, font=("Tahoma", 12))
        self.tf_email.pack(pady=(0, 10))

        self.lbl_password = tk.Label(self, text="Mật khẩu")
        self.lbl_password.pack()
        self.tf_password = tk.Entry(self, show='*', width=40, font=("Tahoma", 12))
        self.tf_password.pack(pady=(0, 10))

        self.btn_login = tk.Button(self, text="ĐĂNG NHẬP", bg="blue", fg="white", command=self.login)
        self.btn_login.pack(pady=(10, 0))

        self.btn_sign_up = tk.Button(self, text="ĐĂNG KÝ", bg="red", fg="white", command=self.open_sign_up)
        self.btn_sign_up.pack(pady=(10, 0))

    def login(self):
        email = self.tf_email.get()
        password = self.tf_password.get()

        if email and password:
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            try:
                response = requests.post(f"{self.SERVER_URL}/login", json={"email": email, "password": hashed_password})
                data = response.json()

                if data["status"] == "SUCCESS":
                    messagebox.showinfo("Notification", data["message"])
                    self.destroy()
                    home_app = ClientHome(email)
                    home_app.mainloop()
                else:
                    messagebox.showwarning("Notification", data["message"])
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            if not email:
                messagebox.showerror("Error", "Email cannot be empty.")
            if not password:
                messagebox.showerror("Error", "Password cannot be empty.")

    def open_sign_up(self):
        self.withdraw()
        sign_up_window = tk.Toplevel(self)
        app = ClientSignUp(sign_up_window)


if __name__ == "__main__":
    app = ClientLogin()
    app.mainloop()
