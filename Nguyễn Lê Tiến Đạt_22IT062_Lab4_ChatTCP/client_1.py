import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

# Kết nối tới server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_server():
    try:
        client.connect(('192.168.1.10', 5555))
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
        root.quit()

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Chat Room")

# Nhãn hiển thị tên người dùng
nickname_label = tk.Label(root, text="", font=("Helvetica", 12))
nickname_label.pack(padx=10, pady=5, anchor='w')

# Tạo khung để hiển thị tin nhắn
chat_window = tk.Text(root, wrap=tk.WORD)
chat_window.config(state=tk.DISABLED)
chat_window.pack(padx=10, pady=10, expand=True, fill='both')

# Thêm thẻ để định dạng màu
chat_window.tag_configure('nickname', foreground='blue', font=('Helvetica', 10, 'bold'))

# Trường nhập tin nhắn
message_entry = tk.Entry(root)
message_entry.pack(padx=10, pady=10, fill='x')

# Nút gửi tin nhắn
def send_message():
    global stop_thread
    message = message_entry.get()  # Lấy tin nhắn từ entry
    if message.strip():
        try:
            if message.startswith('/kick') or message.startswith('/ban'):
                if nickname == 'admin':
                    client.send(message.encode('utf-8'))
                else:
                    chat_window.config(state=tk.NORMAL)
                    chat_window.insert(tk.END, "Commands can only be executed by the admin!\n")
                    chat_window.config(state=tk.DISABLED)
            else:
                client.send(f'{nickname}: {message}'.encode('utf-8'))
            message_entry.delete(0, tk.END)  # Xóa nội dung trong entry sau khi gửi
        except Exception as e:
            chat_window.config(state=tk.NORMAL)
            chat_window.insert(tk.END, f"An error occurred: {e}\n")
            chat_window.config(state=tk.DISABLED)
            client.close()
            stop_thread = True

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(padx=10, pady=10)

stop_thread = False
nickname = None
password = None
receive_thread = None

def receive():
    global stop_thread
    while True:
        if stop_thread:
            break
        try:
            # Nhận tin nhắn từ server
            message = client.recv(1024).decode('utf-8')
            if message == "NICK":
                client.send(nickname.encode('utf-8'))
                next_message = client.recv(1024).decode('utf-8')
                if next_message == 'PASS':
                    client.send(password.encode('utf-8'))
                    if client.recv(1024).decode('utf-8') == 'REFUSE':
                        chat_window.config(state=tk.NORMAL)
                        chat_window.insert(tk.END, "Connection was refused! Wrong password!\n")
                        chat_window.config(state=tk.DISABLED)
                        stop_thread = True
                elif next_message == 'BAN':
                    chat_window.config(state=tk.NORMAL)
                    chat_window.insert(tk.END, "Connection refused because of ban!\n")
                    chat_window.config(state=tk.DISABLED)
                    client.close()
                    stop_thread = True
            else:
                chat_window.config(state=tk.NORMAL)
                parts = message.split(': ', 1)
                if len(parts) == 2:
                    nickname_part, msg_part = parts
                    chat_window.insert(tk.END, f'{nickname_part}: ', 'nickname')
                    chat_window.insert(tk.END, f'{msg_part}\n')
                else:
                    chat_window.insert(tk.END, f'{message}\n')  # Hiển thị tin nhắn trong cửa sổ chat
                chat_window.config(state=tk.DISABLED)
                chat_window.yview(tk.END)
        except Exception as e:
            chat_window.config(state=tk.NORMAL)
            chat_window.insert(tk.END, f"An error occurred: {e}\n")
            chat_window.config(state=tk.DISABLED)
            client.close()
            stop_thread = True
            break

def on_closing():
    global stop_thread, receive_thread
    stop_thread = True
    if receive_thread is not None:
        receive_thread.join()  # Đảm bảo luồng nhận được dừng
    client.close()  # Đóng kết nối socket
    root.quit()  # Thoát ứng dụng Tkinter

# Nhập nickname và mật khẩu nếu là admin
def get_user_info():
    global nickname, password
    nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=root)
    if nickname is None:  # Nếu người dùng hủy nhập nickname
        root.quit()
    elif nickname == 'admin':
        password = simpledialog.askstring("Password", "Enter admin password", parent=root)
        if password is None:  # Nếu người dùng hủy nhập mật khẩu
            root.quit()
    # Cập nhật nhãn hiển thị tên người dùng
    nickname_label.config(text=f"Logged in as: {nickname}")
    root.update_idletasks()  # Đảm bảo giao diện được cập nhật trước khi ẩn cửa sổ

get_user_info()

# Kết nối tới server
connect_to_server()

# Thread để nhận tin nhắn
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Xử lý sự kiện khi đóng cửa sổ
root.protocol("WM_DELETE_WINDOW", on_closing)

# Khởi chạy GUI
root.mainloop()
