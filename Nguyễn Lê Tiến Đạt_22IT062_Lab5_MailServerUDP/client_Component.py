import tkinter as tk
from tkinter import messagebox
import socket
import datetime


class ClientCompose(tk.Tk):
    SERVER_PORT = 2004
    SERVER_ADDRESS = "192.168.232.111"

    def __init__(self, email):
        super().__init__()

        self.title("Soạn thư")
        self.geometry("380x580")

        # Tạo các thành phần giao diện
        self.create_widgets()

        # Lưu địa chỉ email
        self.email = email

    def create_widgets(self):
        # Email người nhận
        tk.Label(self, text="Email người nhận").pack(pady=(10, 0))
        self.tf_email_received = tk.Entry(self)
        self.tf_email_received.pack(pady=(0, 10))

        # Tiêu đề email
        tk.Label(self, text="Tiêu đề").pack(pady=(10, 0))
        self.tf_email_title = tk.Entry(self)
        self.tf_email_title.pack(pady=(0, 10))

        # Nội dung email
        tk.Label(self, text="Nội dung").pack(pady=(10, 0))
        self.ta_content = tk.Text(self, height=15)
        self.ta_content.pack(pady=(0, 10))

        # Nút gửi
        btn_send = tk.Button(self, text="GỬI", command=self.send_message)
        btn_send.pack(pady=(10, 0))

    def send_message(self):
        email_received = self.tf_email_received.get()
        email_title = self.tf_email_title.get()
        content = self.ta_content.get("1.0", tk.END).strip()

        # Kiểm tra tính hợp lệ
        if not email_received:
            messagebox.showerror("Lỗi", "Email người nhận không thể bỏ trống.")
            return
        if not email_title:
            messagebox.showerror("Lỗi", "Tiêu đề không thể bỏ trống.")
            return
        if not content:
            messagebox.showerror("Lỗi", "Nội dung không thể bỏ trống.")
            return

        # Gửi yêu cầu
        now = datetime.datetime.now()
        formatted_date = now.strftime("%d/%m/%Y %H:%M:%S")
        request = f"SEND_EMAIL {email_title}\n{formatted_date}\n{self.email}\n{email_received}\n{content}"

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            try:
                client_socket.sendto(request.encode(), (self.SERVER_ADDRESS, self.SERVER_PORT))

                # Nhận phản hồi từ server
                server_response, _ = client_socket.recvfrom(1024)
                response = server_response.decode()

                command, *msg = response.split(" ", 1)

                if command == "SUCCESS":
                    messagebox.showinfo("Thông báo", "Gửi thư thành công.")
                    self.destroy()
                elif command == "ERROR":
                    messagebox.showwarning("Thông báo", msg[0])

            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể gửi thư: {e}")


if __name__ == "__main__":
    app = ClientCompose("hoangoanhw1@gmail.com")
    app.mainloop()
