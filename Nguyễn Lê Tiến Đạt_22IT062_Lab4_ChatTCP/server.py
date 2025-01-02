import threading
import socket
import tkinter as tk
from os import remove
from tkinter import simpledialog, messagebox

host = '192.168.232.111'
port = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)
clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            client.close()
            remove(client)


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('/kick'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = message[6:].strip()
                    kick_user(name_to_kick)
                else:
                    client.send('You do not have permission to use this command!'.encode('utf-8'))
            elif message.startswith('/ban'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = message[5:].strip()
                    ban_user(name_to_ban)
                else:
                    client.send('You do not have permission to use this command!'.encode('utf-8'))
            else:
                broadcast(message.encode('utf-8'))
                update_chat_window(f'{nicknames[clients.index(client)]}: {message}')  # Cập nhật giao diện với tin nhắn mới
        except Exception as e:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the chat!'.encode('utf-8'))
                update_chat_window(f'{nickname} left the chat!')
                nicknames.remove(nickname)
                update_client_list()  # Cập nhật danh sách client
                break


def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()
        if nickname + '\n' in bans:
            client.send('BAN'.encode('utf-8'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASS'.encode('utf-8'))
            password = client.recv(1024).decode('utf-8')

            if password != 'adminpass':
                client.send('REFUSE'.encode('utf-8'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)
        update_client_list()  # Cập nhật danh sách client
        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
        update_chat_window(f'{nickname} joined the chat!')
        client.send('Connected to the server!'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin!'.encode('utf-8'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin'.encode('utf-8'))
        update_chat_window(f'{name} was kicked by an admin.')
        update_client_list()  # Cập nhật danh sách client


def ban_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_ban = clients[name_index]
        clients.remove(client_to_ban)
        client_to_ban.send('You were banned by an admin!'.encode('utf-8'))
        client_to_ban.close()
        nicknames.remove(name)
        broadcast(f'{name} was banned by an admin'.encode('utf-8'))
        with open('bans.txt', 'a') as f:
            f.write(f'{name}\n')
        update_chat_window(f'{name} was banned by an admin.')
        update_client_list()  # Cập nhật danh sách client


def send_message():
    message = message_entry.get()
    if message.strip():
        try:
            broadcast(f'Server: {message}'.encode('utf-8'))
            update_chat_window(f'Server: {message}')
            message_entry.delete(0, tk.END)
        except Exception as e:
            update_chat_window(f"An error occurred: {e}")


def search_nickname():
    nickname = simpledialog.askstring("Search Nickname", "Enter the nickname of the client:", parent=root)
    if nickname and nickname in nicknames:
        show_action_dialog(nickname)
    else:
        messagebox.showwarning("Warning", "Client not found or not active.")


def show_action_dialog(nickname):
    action = tk.Toplevel(root)
    action.title("Choose Action")

    # Tính toán vị trí căn giữa
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    action_width = 300
    action_height = 200
    x = (root.winfo_screenwidth() // 2) - (action_width // 2)
    y = (root.winfo_screenheight() // 2) - (action_height // 2)
    action.geometry(f'{action_width}x{action_height}+{x}+{y}')

    tk.Label(action, text=f"Choose an action for {nickname}:").pack(padx=10, pady=10)
    tk.Button(action, text="Send Message", command=lambda: send_private_message(nickname)).pack(padx=10, pady=5)
    tk.Button(action, text="Kick User", command=lambda: kick_user_action(nickname)).pack(padx=10, pady=5)
    tk.Button(action, text="Ban User", command=lambda: ban_user_action(nickname)).pack(padx=10, pady=5)
    tk.Button(action, text="Cancel", command=action.destroy).pack(padx=10, pady=5)


def send_private_message(nickname):
    private_message = simpledialog.askstring("Send Private Message", f"Enter your message to {nickname}:", parent=root)
    if private_message:
        recipient_index = nicknames.index(nickname)
        clients[recipient_index].send(f'Private message from server: {private_message}'.encode('utf-8'))
        update_chat_window(f'Sent private message to {nickname}: {private_message}')


def kick_user_action(nickname):
    kick_user(nickname)
    update_chat_window(f'{nickname} has been kicked.')


def ban_user_action(nickname):
    ban_user(nickname)
    update_chat_window(f'{nickname} has been banned.')


def update_chat_window(message):
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, message + '\n')
    chat_window.config(state=tk.DISABLED)
    chat_window.yview(tk.END)


def update_client_list():
    client_list_window.config(state=tk.NORMAL)
    client_list_window.delete(1.0, tk.END)  # Xóa tất cả các mục
    client_list_window.insert(tk.END, "Active Clients:\n", 'tag_red')
    for nickname in nicknames:
        client_list_window.insert(tk.END, f'{nickname} is connecting\n')
    client_list_window.config(state=tk.DISABLED)


# Tạo cửa sổ chính
root = tk.Tk()
root.title("Server Control Panel")

# Nhãn hiển thị tin nhắn
chat_window = tk.Text(root, wrap=tk.WORD, height=20, width=80)
chat_window.config(state=tk.DISABLED)
chat_window.pack(padx=10, pady=10)

# Trường nhập tin nhắn
message_entry = tk.Entry(root)
message_entry.pack(padx=10, pady=5, fill='x')

# Nút gửi tin nhắn
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(padx=10, pady=5)

# Nút tìm nickname
search_button = tk.Button(root, text="Search Nickname", command=search_nickname)
search_button.pack(padx=10, pady=5)

# Danh sách các client
client_list_window = tk.Text(root, wrap=tk.WORD, height=10, width=80)
client_list_window.config(state=tk.DISABLED)
client_list_window.pack(padx=10, pady=10, fill='both', expand=True)

# Thêm thẻ để đổi màu chữ
client_list_window.tag_configure('tag_red', foreground='red', font=('Helvetica', 12, 'bold'))

# Khởi tạo và hiển thị tiêu đề "Active Clients:"
update_client_list()

# Thread để nhận tin nhắn
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Khởi chạy GUI
root.mainloop()
