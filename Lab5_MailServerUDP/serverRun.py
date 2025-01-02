import socket
import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import re

# Các biến toàn cục
SERVER_PORT = 2004
SERVER_ADDRESS = "192.168.232.111"
SERVER_DIR = "ServerFile"


class MailServer:
    def __init__(self, root):
        self.root = root
        self.root.title("Máy chủ (Server)")
        self.root.geometry("700x500")

        self.server_socket = None
        self.is_running = False

        # Giao diện
        self.create_widgets()

    def create_widgets(self):
        self.label_port = tk.Label(self.root, text="Port")
        self.label_port.place(x=80, y=426)

        self.entry_port = tk.Entry(self.root)
        self.entry_port.insert(0, "2004")
        self.entry_port.place(x=115, y=423)

        self.btn_start = tk.Button(self.root, text="Khởi động máy chủ", command=self.start_server)
        self.btn_start.place(x=234, y=422)

        self.btn_stop = tk.Button(self.root, text="Dừng máy chủ", command=self.stop_server, state=tk.DISABLED)
        self.btn_stop.place(x=387, y=422)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='normal')
        self.text_area.place(x=48, y=81, width=587, height=304)

        self.label_title = tk.Label(self.root, text="MAIL APPLICATION", fg="red", font=("Tahoma", 15))
        self.label_title.place(x=251, y=24)

        self.label_role = tk.Label(self.root, text="(Server)", font=("Tahoma", 13))
        self.label_role.place(x=251, y=47)

    def start_server(self):
        if not self.entry_port.get():
            messagebox.showwarning("Thông báo", "Port không thể bỏ trống")
            return

        self.server_port = int(self.entry_port.get())
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.is_running = True

        # Tạo thư mục gốc nếu chưa tồn tại
        os.makedirs(SERVER_DIR, exist_ok=True)

        # Bắt đầu server trong luồng riêng
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

    def list_emails(self, account_name, client_addr):
        account_dir = os.path.join(SERVER_DIR, account_name)

        # Kiểm tra thư mục của tài khoản
        if os.path.exists(account_dir):
            email_files = os.listdir(account_dir)

            if not email_files:
                self.send_response("NO_EMAILS Không có email nào.", client_addr)
            else:
                # Trả về danh sách tên file, ngăn cách bởi dấu phẩy
                response = "SUCCESS " + ",".join(email_files)
                self.send_response(response, client_addr)
        else:
            self.send_response("ERROR Tài khoản không tồn tại.", client_addr)


    def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
        self.log_message(f"Mail Server UDP đang khởi chạy trên port {self.server_port}...")

        while self.is_running:
            receive_data, client_addr = self.server_socket.recvfrom(1024)
            client_request = receive_data.decode('utf-8')
            self.log_message(f"Received: {client_request}")

            request_parts = client_request.split(" ", 2)
            command = request_parts[0]

            try:
                if command == "CREATE_ACCOUNT":
                    self.create_account(request_parts[1], request_parts[2], client_addr)
                elif command == "SEND_EMAIL":
                    request_parts = client_request.split(" ", 1)  # Only split on the first space
                    if len(request_parts) < 2:
                        self.send_response("ERROR Lỗi yêu cầu gửi thư.", client_addr)
                        continue  # Skip to the next iteration of the loop

                    # Split the email details by newlines
                    email_parts = request_parts[1].strip().split("\n")  # Split the second part by newlines
                    if len(email_parts) < 5:  # Check for at least 5 parts
                        self.send_response("ERROR Dữ liệu không đầy đủ.", client_addr)
                        continue  # Skip to the next iteration of the loop

                    # Now send the email parts to the send_message function
                    self.send_message(email_parts[0], email_parts[1], email_parts[2], email_parts[3], email_parts[4],
                                      client_addr)
                elif command == "LOGIN":
                    self.login(request_parts[1], request_parts[2], client_addr)
                elif command == "LIST_EMAILS":  # Thêm xử lý lệnh LIST_EMAILS
                    self.list_emails(request_parts[1], client_addr)
                elif command == "GET_EMAIL":  # Thêm lệnh GET_EMAIL để gửi nội dung email về client
                    self.get_email_content(request_parts[1], request_parts[2], client_addr)
                else:
                    self.log_message(f"Không tìm thấy lệnh: {command}")
            except Exception as e:
                self.log_message(f"Lỗi xử lý yêu cầu: {str(e)}")

    def stop_server(self):
        if self.server_socket:
            self.is_running = False
            self.server_socket.close()
            self.log_message("Server đã dừng.")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

    def create_account(self, account_name, password, client_addr):
        account_dir = os.path.join(SERVER_DIR, account_name)
        if not os.path.exists(account_dir):
            os.makedirs(account_dir)
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Tạo file new_email.txt
            with open(os.path.join(account_dir, "Hello_email.txt"), "w") as new_email_file:
                new_email_file.write("Welcome to Mail!\n")
                new_email_file.write(now + "\n")
                new_email_file.write("admin@gmail.com\n")
                new_email_file.write(account_name + "\n")
                new_email_file.write("Thank you for using this service. We hope that you will feel comfortable.")

            # Tạo file password.txt
            with open(os.path.join(account_dir, "password.txt"), "w") as password_file:
                password_file.write("This is your password!\n")
                password_file.write(now + "\n")
                password_file.write("admin@gmail.com\n")
                password_file.write(account_name + "\n")
                password_file.write(password)

            response = f"SUCCESS Tài khoản {account_name} đã tạo thành công."
            self.send_response(response, client_addr)
        else:
            self.send_response("ERROR Tài khoản đã tồn tại.", client_addr)

    def send_message(self, email_title, formatted_date, email, email_received, content, client_addr):
        account_dir1 = os.path.join(SERVER_DIR, email_received)  # Thư mục của người nhận

        # Kiểm tra sự tồn tại của thư mục người nhận
        if os.path.exists(account_dir1):
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', email_title)
            current_time = int(datetime.now().timestamp() * 1000)
            email_file_path = os.path.join(account_dir1, f"email_{safe_title}.txt")

            # Lưu tệp email chỉ cho người nhận
            with open(email_file_path, "w") as new_email_file:
                new_email_file.write(email_title + "\n")
                new_email_file.write(formatted_date + "\n")
                new_email_file.write(email + "\n")  # Email của người gửi
                new_email_file.write(email_received + "\n")  # Email của người nhận
                new_email_file.write(content)  # Nội dung email

            response = f"SUCCESS Thư đã được gửi thành công từ {email} đến {email_received}."
            self.send_response(response, client_addr)
        else:
            self.send_response("ERROR Tài khoản không tồn tại.", client_addr)

    def login(self, account_name, password, client_addr):
        account_dir = os.path.join(SERVER_DIR, account_name)
        if os.path.exists(account_dir):
            password_file = os.path.join(account_dir, "password.txt")
            try:
                with open(password_file, "r") as reader:
                    lines = reader.readlines()
                    stored_password = lines[4].strip()

                    if stored_password == password:
                        file_names = "\n".join(os.listdir(account_dir))
                        self.log_message(f"{account_name} đã kết nối")
                        self.send_response(f"SUCCESS {file_names}", client_addr)
                    else:
                        self.send_response("ERROR Sai mật khẩu.", client_addr)
            except Exception as e:
                self.send_response("ERROR Không thể đọc mật khẩu.", client_addr)
        else:
            self.send_response("ERROR Tài khoản không tồn tại.", client_addr)

    def send_response(self, response, client_addr):
        if self.server_socket:
            self.server_socket.sendto(response.encode('utf-8'), client_addr)

    def log_message(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, f"{now}: {message}\n")
        self.text_area.configure(state='disabled')

    def get_email_content(self, account_name, file_name, client_addr):
        account_dir = os.path.join(SERVER_DIR, account_name)
        selected_file_path = os.path.join(account_dir, file_name)

        if os.path.isfile(selected_file_path):
            try:
                # Đọc nội dung file email
                with open(selected_file_path, 'r', encoding='utf-8') as file:
                    email_content = file.read()  # Đọc toàn bộ nội dung email
                    response = f"SUCCESS {email_content}"  # Gửi lại email dưới dạng chuỗi
                    self.send_response(response, client_addr)
            except Exception as e:
                self.send_response(f"ERROR Không thể đọc file: {e}", client_addr)
        else:
            self.send_response("ERROR File không tồn tại.", client_addr)


if __name__ == "__main__":
    root = tk.Tk()
    mail_server = MailServer(root)
    root.mainloop()
