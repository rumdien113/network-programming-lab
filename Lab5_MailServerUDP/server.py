import os
import socket
import datetime

SERVER_PORT = 2004
SERVER_DIR = "ServerFile"


def create_account(account_name, password, client_address, server_socket):
    account_dir = os.path.join(SERVER_DIR, account_name)

    if not os.path.exists(account_dir):
        os.makedirs(account_dir)

        # Tạo file new_email.txt
        with open(os.path.join(account_dir, "Hello_email.txt"), "w") as new_email_file:
            now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            new_email_file.write("Welcome to Mail Application!\n")
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
        send_response(response, client_address, server_socket)
    else:
        send_response("ERROR Tài khoản đã tồn tại.", client_address, server_socket)


def login(account_name, password, client_address, server_socket):
    account_dir = os.path.join(SERVER_DIR, account_name)

    if os.path.exists(account_dir):
        with open(os.path.join(account_dir, "password.txt"), "r") as password_file:
            pass_lines = password_file.readlines()
            stored_password = pass_lines[-1].strip()  # Lấy dòng cuối cùng là mật khẩu

        if stored_password == password:
            file_names = "\n".join(os.listdir(account_dir))
            send_response(f"SUCCESS {file_names}", client_address, server_socket)
        else:
            send_response("ERROR Sai mật khẩu.", client_address, server_socket)
    else:
        send_response("ERROR Tài khoản không tồn tại.", client_address, server_socket)


def send_response(response, client_address, server_socket):
    server_socket.sendto(response.encode(), client_address)


def main():
    # Tạo thư mục gốc nếu chưa tồn tại
    if not os.path.exists(SERVER_DIR):
        os.mkdir(SERVER_DIR)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', SERVER_PORT))

    print("Mail Server (UDP) đang khởi chạy...")

    while True:
        # Nhận yêu cầu từ client
        data, client_address = server_socket.recvfrom(1024)
        client_request = data.decode()
        print(f"Received: {client_request}")

        request_parts = client_request.split(" ", 3)
        command = request_parts[0]

        if command == "CREATE_ACCOUNT":
            create_account(request_parts[1], request_parts[2], client_address, server_socket)
        elif command == "LOGIN":
            login(request_parts[1], request_parts[2], client_address, server_socket)
        else:
            print(f"Không tìm thấy lệnh: {command}")


if __name__ == "__main__":
    main()
