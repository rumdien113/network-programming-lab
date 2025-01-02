import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

# Kết nối tới server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_server():
    try:
        client.connect(('192.168.232.111', 5556))
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
        root.quit()

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Chat Room")

# Khung hiển thị danh sách nickname
left_frame = tk.Frame(root, width=200, bg="lightgray")
left_frame.pack(side=tk.LEFT, fill=tk.Y)

nickname_label = tk.Label(left_frame, text="Online Users", font=("Helvetica", 12))
nickname_label.pack(padx=10, pady=5)

# Listbox để hiển thị các nickname của người dùng khác
users_listbox = tk.Listbox(left_frame)
users_listbox.pack(padx=10, pady=10, expand=True, fill='both')

# Listbox để hiển thị các nhóm
groups_label = tk.Label(left_frame, text="Groups", font=("Helvetica", 12))
groups_label.pack(padx=10, pady=5)

groups_listbox = tk.Listbox(left_frame)
groups_listbox.pack(padx=10, pady=10, expand=True, fill='both')

# Khung hiển thị tin nhắn chat
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Tạo khung để hiển thị tin nhắn
chat_window = tk.Text(right_frame, wrap=tk.WORD)
chat_window.config(state=tk.DISABLED)
chat_window.pack(padx=10, pady=10, expand=True, fill='both')

# Trường nhập tin nhắn
message_entry = tk.Entry(right_frame)
message_entry.pack(padx=10, pady=10, fill='x')

# Lưu nickname người nhận tin nhắn riêng tư
private_recipient = None

# Hàm gửi tin nhắn
def send_message():
    message = message_entry.get()
    if message.strip():
        try:
            if private_recipient:  # Kiểm tra xem có người nhận tin nhắn riêng không
                client.send(f'/msg {private_recipient}: {message}'.encode('utf-8'))
            elif groups_listbox.curselection():  # Nhắn tin đến nhóm
                selected_group = groups_listbox.get(groups_listbox.curselection())
                client.send(f'/group {selected_group}: {message}'.encode('utf-8'))
            else:
                client.send(f'{nickname}: {message}'.encode('utf-8'))
            message_entry.delete(0, tk.END)
        except Exception as e:
            chat_window.config(state=tk.NORMAL)
            chat_window.insert(tk.END, f"An error occurred: {e}\n")
            chat_window.config(state=tk.DISABLED)
            client.close()

send_button = tk.Button(right_frame, text="Send", command=send_message)
send_button.pack(padx=10, pady=10)

create_group_button = tk.Button(left_frame, text="Create Group", command=lambda: create_group())
create_group_button.pack(padx=10, pady=5)

join_group_button = tk.Button(left_frame, text="Join Group", command=lambda: join_group())
join_group_button.pack(padx=10, pady=5)

leave_group_button = tk.Button(left_frame, text="Leave Group", command=lambda: leave_group())
leave_group_button.pack(padx=10, pady=5)

stop_thread = False
nickname = None

# Hàm cập nhật danh sách người dùng
def update_user_list(users):
    users_listbox.delete(0, tk.END)
    for user in users:
        users_listbox.insert(tk.END, user)

# Hàm cập nhật danh sách nhóm
def update_group_list(groups):
    groups_listbox.delete(0, tk.END)
    for group in groups:
        groups_listbox.insert(tk.END, group)

# Hàm khi nhấp vào nickname
def on_user_select(event):
    global private_recipient
    selected_user_index = users_listbox.curselection()
    if selected_user_index:
        private_recipient = users_listbox.get(selected_user_index)
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, f"Selected user for private message: {private_recipient}\n")
        chat_window.config(state=tk.DISABLED)

# Gán sự kiện nhấp chuột cho Listbox
users_listbox.bind("<<ListboxSelect>>", on_user_select)

def create_group():
    group_name = simpledialog.askstring("Create Group", "Enter group name:", parent=root)
    if group_name:
        client.send(f'/create_group {group_name}'.encode('utf-8'))

def join_group():
    selected_group_index = groups_listbox.curselection()
    if selected_group_index:
        selected_group = groups_listbox.get(selected_group_index)
        client.send(f'/join_group {selected_group}'.encode('utf-8'))

def leave_group():
    selected_group_index = groups_listbox.curselection()
    if selected_group_index:
        selected_group = groups_listbox.get(selected_group_index)
        client.send(f'/leave_group {selected_group}'.encode('utf-8'))

def receive():
    global stop_thread
    while True:
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "NICK":
                client.send(nickname.encode('utf-8'))
            elif message.startswith("USER_LIST:"):
                users = message[len("USER_LIST:"):].split(",")
                update_user_list(users)
            elif message.startswith("GROUP_LIST:"):
                groups = message[len("GROUP_LIST:"):].split(",")
                update_group_list(groups)
            elif message.startswith("GROUP_MESSAGE_"):
                parts = message.split(': ', 2)
                chat_window.config(state=tk.NORMAL)
                chat_window.insert(tk.END, f'GROUP {parts[1]}: {parts[2]}\n')
                chat_window.config(state=tk.DISABLED)
                chat_window.yview(tk.END)
            else:
                chat_window.config(state=tk.NORMAL)
                parts = message.split(': ', 1)
                if len(parts) == 2:
                    nickname_part, msg_part = parts
                    chat_window.insert(tk.END, f'{nickname_part}: ', 'nickname')
                    chat_window.insert(tk.END, f'{msg_part}\n')
                else:
                    chat_window.insert(tk.END, f'{message}\n')
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
    global stop_thread
    stop_thread = True
    client.close()
    root.quit()

# Nhập nickname
def get_user_info():
    global nickname
    nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=root)
    if nickname is None:
        root.quit()

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