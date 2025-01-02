import threading
import socket

host = '192.168.232.111'
port = 5556

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)
clients = []
nicknames = []
groups = {}

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            client.close()
            if client in clients:
                clients.remove(client)

def handle(client, nickname):
    user_groups = []
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('/msg'):
                recipient, msg = message[5:].split(': ', 1)
                send_private_message(nickname, recipient, msg)
            elif message.startswith('/group'):
                group_name, msg = message[7:].split(': ', 1)
                send_group_message(nickname, group_name, msg)
            elif message.startswith('/create_group'):
                group_name = message[14:]
                user_groups.append(group_name)
                create_group(nickname, group_name)
            elif message.startswith('/join_group'):
                group_name = message[12:]
                user_groups.append(group_name)
                join_group(nickname, group_name)
            elif message.startswith('/leave_group'):
                group_name = message[13:]
                user_groups.remove(group_name)
                leave_group(nickname, group_name)
            else:
                broadcast(f'{nickname}: {message}'.encode('utf-8'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            broadcast(f'{nickname} left the chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            send_nickname_list()
            break

def send_private_message(sender_nickname, recipient, message):
    if recipient in nicknames:
        recipient_index = nicknames.index(recipient)
        clients[recipient_index].send(f'Private message from {sender_nickname}: {message}'.encode('utf-8'))

def send_group_message(sender_nickname, group_name, message):
    if group_name in groups:
        for member in groups[group_name]:
            if member in nicknames:
                index = nicknames.index(member)
                clients[index].send(f'GROUP_MESSAGE_{group_name}: {sender_nickname}: {message}'.encode('utf-8'))

def create_group(creator_nickname, group_name):
    if group_name not in groups:
        groups[group_name] = [creator_nickname]
        broadcast(f'Group {group_name} created by {creator_nickname}!'.encode('utf-8'))
        send_group_list()

def join_group(nickname, group_name):
    if group_name in groups:
        if nickname not in groups[group_name]:
            groups[group_name].append(nickname)
            broadcast(f'{nickname} joined group {group_name}!'.encode('utf-8'))
            send_group_list()

def leave_group(nickname, group_name):
    if group_name in groups and nickname in groups[group_name]:
        groups[group_name].remove(nickname)
        broadcast(f'{nickname} left group {group_name}!'.encode('utf-8'))
        send_group_list()

def send_group_list():
    group_list = ','.join(groups.keys())
    for client in clients:
        try:
            client.send(f'GROUP_LIST:{group_list}'.encode('utf-8'))
        except:
            client.close()
            if client in clients:
                clients.remove(client)

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
        send_nickname_list()
        send_group_list()

        thread = threading.Thread(target=handle, args=(client, nickname))
        thread.start()

def send_nickname_list():
    nickname_list = ','.join(nicknames)
    for client in clients:
        try:
            client.send(f'USER_LIST:{nickname_list}'.encode('utf-8'))
        except:
            client.close()
            if client in clients:
                clients.remove(client)

# Chạy máy chủ
print("Server is running...")
receive()