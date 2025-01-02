# client_signup.py
import tkinter as tk
from tkinter import messagebox
import socket
import hashlib

class ClientSignUp(tk.Toplevel):  # Sử dụng Toplevel để mở cửa sổ mới
    SERVER_ADDRESS = '192.168.232.111'
    SERVER_PORT = 2004

    def __init__(self, master):
        super().__init__(master)  # Tạo cửa sổ con từ master
        self.title("Đăng ký (Client)")
        self.geometry("600x330")

        # Tiêu đề
        self.lbl_title = tk.Label(self, text="MAIL APPLICATION", fg="red", font=("Tahoma", 15, "bold"))
        self.lbl_title.pack(pady=(10, 0))

        # Hướng dẫn
        self.lbl_heading = tk.Label(self, text="Tạo tài khoản mới", font=("Tahoma", 13))
        self.lbl_heading.pack()

        # Nhập email
        self.lbl_email = tk.Label(self, text="Email")
        self.lbl_email.pack()
        self.tf_email = tk.Entry(self, width=40,font=("Tahoma", 12))
        self.tf_email.pack(pady=(0, 10))
        # self.tf_email.pack()

        # Nhập mật khẩu
        self.lbl_password = tk.Label(self, text="Mật khẩu")
        self.lbl_password.pack()
        self.tf_password = tk.Entry(self, show='*', width=40,font=("Tahoma", 12))
        self.tf_password.pack(pady=(0, 10))


        # Nhập lại mật khẩu
        self.lbl_re_password = tk.Label(self, text="Nhập lại mật khẩu")
        self.lbl_re_password.pack()
        self.tf_re_password = tk.Entry(self, show='*', width=40,font=("Tahoma", 12))
        self.tf_re_password.pack(pady=(0, 10))


        # Nút đăng ký
        self.btn_sign_up = tk.Button(self, text="ĐĂNG KÝ", command=self.create_account)
        self.btn_sign_up.pack(pady=(10, 0))

        # Nút quay lại đăng nhập
        self.btn_back_login = tk.Button(self, text="VỀ ĐĂNG NHẬP", command=self.back_to_login)
        self.btn_back_login.pack(pady=(10, 0))

    def create_account(self):
        email = self.tf_email.get()
        password = self.tf_password.get()
        re_password = self.tf_re_password.get()

        if email and password:
            if password == re_password:
                # Mã hóa mật khẩu
                hashed_password = hashlib.md5(password.encode()).hexdigest()

                # Gửi yêu cầu đến server
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
                    request = f"CREATE_ACCOUNT {email} {hashed_password}"
                    client_socket.sendto(request.encode(), (self.SERVER_ADDRESS, self.SERVER_PORT))

                    # Nhận phản hồi từ server
                    response, _ = client_socket.recvfrom(1024)
                    response = response.decode()

                    # Xử lý phản hồi
                    request_parts = response.split(" ", 1)
                    command = request_parts[0]

                    if command == "SUCCESS":
                        messagebox.showinfo("Thông báo", request_parts[1])
                        self.back_to_login()
                    elif command == "ERROR":
                        messagebox.showwarning("Thông báo", request_parts[1])
            else:
                messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp.")
        else:
            messagebox.showerror("Lỗi", "Email và mật khẩu không thể bỏ trống.")

    def back_to_login(self):
        self.destroy()  # Đóng cửa sổ đăng ký và trở về cửa sổ đăng nhập
        self.master.master.deiconify()