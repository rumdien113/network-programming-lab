import tkinter as tk
from tkinter import messagebox
import requests
import datetime


class ClientCompose(tk.Toplevel):
    SERVER_URL = "http://192.168.232.111:5000"

    def __init__(self, email):
        super().__init__()
        self.email = email
        self.title("Compose Email")
        self.geometry("600x450")

        self.lbl_to = tk.Label(self, text="To:")
        self.lbl_to.pack()
        self.tf_to = tk.Entry(self, width=50)
        self.tf_to.pack(pady=(0, 10))

        self.lbl_title = tk.Label(self, text="Title:")
        self.lbl_title.pack()
        self.tf_title = tk.Entry(self, width=50)
        self.tf_title.pack(pady=(0, 10))

        self.lbl_content = tk.Label(self, text="Content:")
        self.lbl_content.pack()
        self.ta_content = tk.Text(self, width=50, height=10)
        self.ta_content.pack(pady=(0, 10))

        self.btn_send = tk.Button(self, text="SEND", bg="blue", fg="white", command=self.send_email)
        self.btn_send.pack(pady=(10, 0))

    def send_email(self):
        to_email = self.tf_to.get()
        title = self.tf_title.get()
        content = self.ta_content.get("1.0", tk.END).strip()
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        ip = requests.get('https://api.ipify.org').text

        if to_email and title and content:
            try:
                response = requests.post(f"{self.SERVER_URL}/send_email", json={
                    "from_email": self.email,
                    "to_email": to_email,
                    "time": current_time,
                    "title": title,
                    "content": content,
                    "ip": ip,
                })
                data = response.json()
                print(data)
                print(content)

                if data["status"] == "SUCCESS":
                    messagebox.showinfo("Notification", data["message"])
                    self.destroy()
                else:
                    messagebox.showwarning("Notification", data["message"])
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showerror("Error", "All fields must be filled.")