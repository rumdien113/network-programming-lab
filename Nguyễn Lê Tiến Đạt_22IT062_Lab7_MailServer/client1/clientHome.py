import tkinter as tk
import requests
from tkinter import messagebox, scrolledtext, Listbox, Scrollbar
from client_Component import ClientCompose


class ClientHome(tk.Tk):
    SERVER_PORT = 5000
    SERVER_URL = "http://192.168.232.111:5000"
    POLL_INTERVAL = 5000

    def __init__(self, email):
        super().__init__()
        self.listbox = None
        self.email = email
        self.title(f" You are logged in with an email account: {email}")
        self.geometry("850x500")

        # Tạo các thành phần giao diện
        self.create_widgets()

        self.poll_for_new_emails()

    def create_widgets(self):
        # Nút "Thư mới"
        btn_start = tk.Button(self, text="New", font=("Tahoma", 14), bg= "gray", command=self.compose_email)
        btn_start.place(x=10, y=10, width=170, height=40)

        # Refresh Email button
        btn_refresh = tk.Button(self, text="Refresh", font=("Tahoma", 14), bg="gray", command=self.populate_email_list)
        btn_refresh.place(x=190, y=10, width=170, height=40)

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
        self.lbl_email_title.place(x=190, y=55)

        self.lbl_time = tk.Label(self, text="Time:", anchor="w")
        self.lbl_time.place(x=190, y=85)

        self.lbl_ip = tk.Label(self, text="Ip:", anchor="w")
        self.lbl_ip.place(x=190, y=110)

        self.lbl_from = tk.Label(self, text="From:", anchor="w")
        self.lbl_from.place(x=190, y=135)

        self.lbl_to = tk.Label(self, text="To:", anchor="w")
        self.lbl_to.place(x=190, y=160)

        self.ta_info = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='normal')
        self.ta_info.place(x=190, y=185, width=636, height=291)

        lbl_title = tk.Label(self, text="MAIL APPLICATION", fg="red", font=("Tahoma", 15, "bold"), anchor="center")
        lbl_title.place(x=445, y=10)

    def populate_email_list(self):
        self.listbox.delete(0, tk.END)
        response = requests.get(f"{self.SERVER_URL}/list_emails", params={"email": self.email})
        data = response.json()

        if data["status"] == "SUCCESS":
            for i in data["emails"]:
                self.listbox.insert(tk.END, i)
        elif data["status"] == "NO_EMAILS":
            pass
            # messagebox.showinfo("Notification", "No emails found.")
        else:
            messagebox.showerror("Error", "Error fetching email list.")

    def on_select_email(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_email = self.listbox.get(selected_index)
            self.request_email_content(selected_email)

    def request_email_content(self, email):
        response = requests.get(f"{self.SERVER_URL}/get_email", params={"title": email})
        data = response.json()
        print(data)

        if data["status"] == "SUCCESS":
            self.display_email_content(data["email"])
        else:
            messagebox.showerror("Error", "Error fetching email content.")

    def display_email_content(self, email_data):
        try:
            from_email = email_data[2]
            to_email = email_data[1]
            time = email_data[3]
            title = email_data[4]
            content = email_data[5]
            ip = email_data[6]

            self.lbl_email_title.config(text=f"Title: {title}")
            self.lbl_time.config(text=f"Time: {time}")
            self.lbl_ip.config(text=f"Ip: {ip}")
            self.lbl_from.config(text=f"From: {from_email}")
            self.lbl_to.config(text=f"To: {to_email}")
            self.ta_info.delete(1.0, tk.END)
            self.ta_info.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying email content: {e}")

    def compose_email(self):
        # messagebox.showinfo("Compose Email", "Open new compose window")
        compose_window = ClientCompose(self.email)
        compose_window.mainloop()

    def poll_for_new_emails(self):
        self.populate_email_list()
        self.after(self.POLL_INTERVAL, self.poll_for_new_emails)


if __name__ == "__main__":
    email = "dat@gmail.com"
    app = ClientHome(email)
    app.mainloop()
# with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
#     request = f"LIST_EMAILS\n{self.email}"
#     client_socket.sendto(request.encode(), (self.SERVER_ADDRESS, self.SERVER_PORT))
#
#     response, _ = client_socket.recvfrom(4096)
#     response = response.decode()
#
#     if response.startswith("SUCCESS"):
#         emails = response.split(" ", 1)[1].split(",")
#         for email in emails:
#             self.listbox.insert(tk.END, email)
#     elif response.startswith("NO_EMAILS"):
#         messagebox.showinfo("Notification", "No emails found.")
#     else:
#         messagebox.showerror("Error", "Error fetching email list.")
#
#     def on_select_email(self, event):
#         selected_index = self.listbox.curselection()
#         if selected_index:
#             selected_email = self.listbox.get(selected_index)
#             self.request_email_content(selected_email)
#
#     def request_email_content(self, email):
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
#             request = f"GET_EMAIL\n{email}"
#             client_socket.sendto(request.encode(), (self.SERVER_ADDRESS, self.SERVER_PORT))
#
#             response, _ = client_socket.recvfrom(4096)
#             response = response.decode()
#
#             if response.startswith("SUCCESS"):
#                 email_content = response.split(" ", 1)[1]
#                 self.display_email_content(email_content)
#             else:
#                 messagebox.showerror("Error", "Error fetching email content.")
#
#     def display_email_content(self, email_data):
#         try:
#             # Ensure email_data is a list of tuples
#             if isinstance(email_data, str):
#                 email_data = eval(email_data)
#
#             # Extract the first tuple from the list
#             email_data = email_data[0]
#
#             from_email = email_data[0]
#             to_email = email_data[1]
#             time = email_data[2].strftime("%Y-%m-%d %H:%M:%S")
#             title = email_data[3]
#             content = email_data[4]
#
#             self.lbl_email_title.config(text=f"Title: {title}")
#             self.lbl_time.config(text=f"Time: {time}")
#             self.lbl_from.config(text=f"From: {from_email}")
#             self.lbl_to.config(text=f"To: {to_email}")
#             self.ta_info.delete(1.0, tk.END)
#             self.ta_info.insert(tk.END, content)
#         except Exception as e:
#             messagebox.showerror("Error", f"Error displaying email content: {e}")
#
#     def compose_email(self):
#         messagebox.showinfo("Compose Email", "Mở cửa sổ soạn thư mới")
#         compose_window = ClientCompose(self.email)  # Mở cửa sổ soạn thư
#         compose_window.mainloop()  # Chạy cửa sổ soạn thư
#
#
# if __name__ == "__main__":
#     email = "hoangoanhw1@gmail.com"
#     app = ClientHome(email)
#     app.mainloop()
