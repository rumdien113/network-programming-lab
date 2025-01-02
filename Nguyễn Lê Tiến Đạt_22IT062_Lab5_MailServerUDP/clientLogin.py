# client_login.py
import tkinter as tk
from tkinter import messagebox
import socket
import hashlib
from clientSignUp import ClientSignUp  # Import lớp ClientSignUp từ file client_signup.py
from clientHome import ClientHome
class ClientLogin(tk.Tk):
    SERVER_ADDRESS = '192.168.232.111'
    SERVER_PORT = 2004

    def __init__(self):
        super().__init__()
        self.title("Đăng nhập (Client)")
        self.geometry("600x275")

        # Tiêu đề
        self.lbl_title = tk.Label(self, text="MAIL APPLICATION", fg="red", font=("Tahoma", 15, "bold"))
        self.lbl_title.pack(pady=(10, 0))

        # Hướng dẫn
        self.lbl_heading = tk.Label(self, text="Đăng nhập", font=("Tahoma", 13))
        self.lbl_heading.pack()

        # Nhập email
        self.lbl_email = tk.Label(self, text="Email")
        self.lbl_email.pack()
        self.tf_email = tk.Entry(self, width=40, font=("Tahoma", 12))  # Thay đổi kích thước ô nhập email
        self.tf_email.pack(pady=(0, 10))  # Thêm khoảng cách phía dưới

        # Nhập mật khẩu
        self.lbl_password = tk.Label(self, text="Mật khẩu")
        self.lbl_password.pack()
        self.tf_password = tk.Entry(self, show='*', width=40,font=("Tahoma", 12))  # Thay đổi kích thước ô nhập mật khẩu
        self.tf_password.pack(pady=(0, 10))  # Thêm khoảng cách phía dưới

        # Nút đăng nhập
        self.btn_login = tk.Button(self, text="ĐĂNG NHẬP", bg= "blue", fg="white", command=self.login)
        self.btn_login.pack(pady=(10, 0))

        # Nút đăng ký
        self.btn_sign_up = tk.Button(self, text="ĐĂNG KÝ", bg= "red", fg="white" ,command=self.open_sign_up)
        self.btn_sign_up.pack(pady=(10, 0))

    def login(self):
        email = self.tf_email.get()
        password = self.tf_password.get()

        if email and password:
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            request = f"LOGIN {email} {hashed_password}"

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
                    client_socket.sendto(request.encode(), (self.SERVER_ADDRESS, self.SERVER_PORT))

                    # Nhận phản hồi từ server
                    server_response, _ = client_socket.recvfrom(1024)
                    response = server_response.decode()

                    request_parts = response.split(" ", 1)
                    command = request_parts[0]

                    if command == "SUCCESS":
                        messagebox.showinfo("Thông báo", "Đăng nhập thành công.")
                        # Chuyển sang giao diện chính sau khi đăng nhập thành công
                        self.destroy()  # Đóng cửa sổ đăng nhập
                        # Hiển thị giao diện ClientHome
                        file_names = "new_email.txt\npassword.txt"  # Danh sách email có thể lấy từ server
                        home_app = ClientHome(email, file_names)  # Khởi tạo giao diện ClientHome
                        home_app.mainloop()  # Chạy giao diện ClientHome
                    elif command == "ERROR":
                        messagebox.showwarning("Thông báo", request_parts[1])
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
        else:
            if not email:
                messagebox.showerror("Lỗi", "Email không thể bỏ trống.")
            if not password:
                messagebox.showerror("Lỗi", "Mật khẩu không thể bỏ trống.")

    def open_sign_up(self):
        self.withdraw() # Ẩn cửa sổ đăng nhập hiện tại
        sign_up_window = tk.Toplevel(self)  # Tạo cửa sổ mới cho đăng ký
        app = ClientSignUp(sign_up_window)  # Khởi tạo đối tượng ClientSignUp từ file khác


if __name__ == "__main__":
    app = ClientLogin()
    app.mainloop()
