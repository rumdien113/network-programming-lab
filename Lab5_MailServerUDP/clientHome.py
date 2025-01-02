import os
import tkinter as tk
import socket
from tkinter import messagebox, filedialog, scrolledtext, Listbox, Scrollbar
from client_Component import ClientCompose


class ClientHome(tk.Tk):
    SERVER_DIR = "ServerFile"
    SERVER_PORT = 2004
    SERVER_ADDRESS = "192.168.232.111"

    def __init__(self, email, file_names):
        super().__init__()
        self.email = email
        self.file_names = file_names.split("\n")
        self.title(f" You are logged in with an email account: {email}")
        self.geometry("850x500")

        # Tạo các thành phần giao diện
        self.create_widgets()

    def create_widgets(self):
        # Nút "Thư mới"
        btn_start = tk.Button(self, text="New", font=("Tahoma", 14), bg= "gray", command=self.compose_email)
        btn_start.place(x=10, y=10, width=170, height=40)

        # Danh sách email
        self.listbox = Listbox(self)
        self.listbox.bind("<<ListboxSelect>>", self.on_select_email)
        self.populate_email_list()

        # Thanh cuộn cho danh sách
        scroll_bar = Scrollbar(self)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.listbox.yview)

        self.listbox.place(x=10, y=60, width=170, height=393)

        # Nhãn và khu vực hiển thị thông tin email
        self.lbl_email_title = tk.Label(self, text="Title:", font=("Tahoma", 15, "bold"), anchor="w")
        self.lbl_email_title.place(x=190, y=62)

        self.lbl_time = tk.Label(self, text="Time:", anchor="w")
        self.lbl_time.place(x=190, y=85)

        self.lbl_from = tk.Label(self, text="From:", anchor="w")
        self.lbl_from.place(x=190, y=110)

        self.lbl_to = tk.Label(self, text="To:", anchor="w")
        self.lbl_to.place(x=190, y=137)

        self.ta_info = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='normal')
        self.ta_info.place(x=190, y=162, width=636, height=291)

        lbl_title = tk.Label(self, text="MAIL APPLICATION", fg="red", font=("Tahoma", 15, "bold"), anchor="center")
        lbl_title.place(x=445, y=10)

    def populate_email_list(self):
        self.listbox.delete(0, tk.END)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            request = f"LIST_EMAILS {self.email}"
            client_socket.sendto(request.encode(), (self.SERVER_ADDRESS, self.SERVER_PORT))

            response, _ = client_socket.recvfrom(1024)
            response = response.decode()

            if response.startswith("SUCCESS"):
                # Cập nhật self.file_names
                self.file_names = response.split(" ", 1)[1].split(",")
                # Hiển thị các file email trong listbox
                for file_name in self.file_names:
                    self.listbox.insert(tk.END, file_name)
            elif response.startswith("NO_EMAILS"):
                messagebox.showinfo("Thông báo", "Không có email nào.")
            else:
                messagebox.showerror("Error", "Lỗi trong quá trình lấy danh sách email.")

    def on_select_email(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_file = self.file_names[selected_index[0]]  # Cập nhật để lấy tên file từ self.file_names
            self.request_email_content(selected_file)  # Gửi yêu cầu tới server

    def request_email_content(self, file_name):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            request = f"GET_EMAIL {self.email} {file_name}"  # Gửi yêu cầu lấy nội dung email
            client_socket.sendto(request.encode(), (self.SERVER_ADDRESS, self.SERVER_PORT))

            response, _ = client_socket.recvfrom(4096)  # Tăng kích thước bộ đệm để nhận nhiều dữ liệu hơn
            response = response.decode()

            if response.startswith("SUCCESS"):
                # Giữ nguyên dòng đầu tiên để lấy tiêu đề email
                email_content = response[response.index(" ") + 1:]  # Bỏ qua từ "SUCCESS"
                self.display_email_content(email_content)
            else:
                messagebox.showerror("Error", "Lỗi khi tải email từ server.")

    def display_email_content(self, email_content):
        lines = email_content.split("\n")
        if len(lines) >= 4:
            self.lbl_email_title.config(text=f"Title: {lines[0].strip()}")
            self.lbl_time.config(text=f"Time: {lines[1].strip()}")
            self.lbl_from.config(text=f"From: {lines[2].strip()}")
            self.lbl_to.config(text=f"To: {lines[3].strip()}")
            self.ta_info.delete(1.0, tk.END)
            self.ta_info.insert(tk.END, "".join(lines[4:]).strip())  # Hiển thị nội dung email
        else:
            messagebox.showwarning("Warning", "Định dạng email không chính xác.")

    def compose_email(self):
        messagebox.showinfo("Compose Email", "Mở cửa sổ soạn thư mới")
        compose_window = ClientCompose(self.email)  # Mở cửa sổ soạn thư
        compose_window.mainloop()  # Chạy cửa sổ soạn thư


if __name__ == "__main__":
    email = "hoangoanhw1@gmail.com"
    file_names = "Hello_email.txt\npassword.txt"
    app = ClientHome(email, file_names)
    app.mainloop()
