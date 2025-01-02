import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        dbname="mail_server",
        user="tiendat",
        password="180104",
        host="localhost"
    )


@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    email = data['email']
    password = data['password']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "SUCCESS", "message": "Account created successfully"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        if res and res[0] == password:
            return jsonify({"status": "SUCCESS", "message": "Login successfully"})
        else:
            return jsonify({"status": "ERROR", "message": "Invalid email or password"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.json
    from_email = data['from_email']
    to_email = data['to_email']
    time = data['time']
    title = data['title']
    content = data['content']
    ip = data['ip']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO emails (from_email, to_email, time, title, content, ip) VALUES (%s, %s, %s, %s, %s, %s)",
            (from_email, to_email, time, title, content, ip)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "SUCCESS", "message": "Email sent successfully"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


@app.route('/list_emails', methods=['GET'])
def list_emails():
    curr_email = request.args.get('email')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM emails WHERE to_email = %s", (curr_email,))
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        if res:
            emails = [row[0] for row in res]
            return jsonify({"status": "SUCCESS", "emails": emails})
        else:
            return jsonify({"status": "NO_EMAILS", "message": "No emails found"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


@app.route('/get_email', methods=['GET'])
def get_email():
    title = request.args.get('title')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails WHERE title = %s", (title,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        if res:
            return jsonify({"status": "SUCCESS", "email": res})
        else:
            return jsonify({"status": "ERROR", "message": "Email not found"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


SERVER_PORT = 5000
SERVER_ADDRESS = '192.168.232.111'

if __name__ == '__main__':
    app.run(host=SERVER_ADDRESS, port=SERVER_PORT)


# def handle_rerquest(data):
#     try:
#         connect = psycopg2.connect(
#             dbname="mail_server",
#             user="tiendat",
#             password="180104",
#             host="localhost"
#         )
#         cursor = connect.cursor()
#
#         request_parts = data.split("\n")
#         command = request_parts[0]
#         print(f"Received: {command}")
#         print(request_parts)
#
#         if command == "CREATE_ACCOUNT":
#             email = request_parts[1]
#             pw = request_parts[2]
#
#             cursor.execute(
#                 "INSERT INTO users (email, password) VALUES (%s, %s)",
#                 (email, pw)
#             )
#             connect.commit()
#             response = "SUCCESS Account created successfully"
#
#         elif command == "LOGIN":
#             email = request_parts[1]
#             pw = request_parts[2]
#
#             cursor.execute(
#                 "SELECT password FROM users WHERE email = %s",
#                 (email,)
#             )
#             result = cursor.fetchone()
#
#             if result and result[0] == pw:
#                 response = "SUCCESS Login successfully"
#             else:
#                 response = "ERROR Invalid email or password"
#
#         elif command == "SEND_EMAIL":
#             from_email = request_parts[1]
#             to_email = request_parts[2]
#             time = request_parts[3]
#             title = request_parts[4]
#             content = request_parts[5]
#
#             cursor.execute(
#                 "INSERT INTO emails (from_email, to_email, time, title, content) VALUES (%s, %s, %s, %s, %s)",
#                 (from_email, to_email, time, title, content)
#             )
#             connect.commit()
#             response = "SUCCESS Email sent successfully"
#
#         elif command == "LIST_EMAILS":
#             curr_email = request_parts[1]
#
#             cursor.execute(
#                 "SELECT title FROM emails WHERE to_email = %s",
#                 (curr_email,)
#             )
#             result = cursor.fetchall()
#
#             if result:
#                 emails = ",".join(row[0] for row in result)
#                 response = f"SUCCESS {emails}"
#
#         elif command == "GET_EMAIL":
#             title = request_parts[1]
#
#             cursor.execute(
#                 "SELECT from_email, to_email, time, title, content FROM emails WHERE title = %s",
#                 (title,)
#             )
#             infomation = cursor.fetchall()
#             if infomation:
#                 response = f"SUCCESS {infomation}"
#             else:
#                 response = "ERROR Email not found"
#             print(response)
#
#         elif command == "SEND_EMAIL":
#             from_email = request_parts[1]
#             to_email = request_parts[2]
#             time = request_parts[3]
#             title = request_parts[4]
#             content = request_parts[5]
#
#             cursor.execute(
#                 "INSERT INTO emails (from_email, to_email, time, title, content) VALUES (%s, %s, %s, %s, %s, %s)",
#                 (from_email, to_email, time, title, content)
#             )
#             connect.commit()
#             response = "SUCCESS Email sent successfully"
#
#
#         else:
#             response = "ERROR Unknow comman"
#
#         cursor.close()
#         connect.close()
#     except psycopg2.Error as e:
#         response = f"ERROR Database error: {e}"
#     except Exception as e:
#         response = f"ERROR An error occurred: {e}"
#
#     return response


# def create_account(account_name, password, client_address, server_socket):
#     account_dir = os.path.join(SERVER_DIR, account_name)
#
#     if not os.path.exists(account_dir):
#         os.makedirs(account_dir)
#
#         # Tạo file new_email.txt
#         with open(os.path.join(account_dir, "Hello_email.txt"), "w") as new_email_file:
#             now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#             new_email_file.write("Welcome to Mail Application!\n")
#             new_email_file.write(now + "\n")
#             new_email_file.write("admin@gmail.com\n")
#             new_email_file.write(account_name + "\n")
#             new_email_file.write("Thank you for using this service. We hope that you will feel comfortable.")
#
#         # Tạo file password.txt
#         with open(os.path.join(account_dir, "password.txt"), "w") as password_file:
#             password_file.write("This is your password!\n")
#             password_file.write(now + "\n")
#             password_file.write("admin@gmail.com\n")
#             password_file.write(account_name + "\n")
#             password_file.write(password)
#
#         response = f"SUCCESS Tài khoản {account_name} đã tạo thành công."
#         send_response(response, client_address, server_socket)
#     else:
#         send_response("ERROR Tài khoản đã tồn tại.", client_address, server_socket)
#
#
# def login(account_name, password, client_address, server_socket):
#     account_dir = os.path.join(SERVER_DIR, account_name)
#
#     if os.path.exists(account_dir):
#         with open(os.path.join(account_dir, "password.txt"), "r") as password_file:
#             pass_lines = password_file.readlines()
#             stored_password = pass_lines[-1].strip()  # Lấy dòng cuối cùng là mật khẩu
#
#         if stored_password == password:
#             file_names = "\n".join(os.listdir(account_dir))
#             send_response(f"SUCCESS {file_names}", client_address, server_socket)
#         else:
#             send_response("ERROR Sai mật khẩu.", client_address, server_socket)
#     else:
#         send_response("ERROR Tài khoản không tồn tại.", client_address, server_socket)
#
#
# def send_response(response, client_address, server_socket):
#     server_socket.sendto(response.encode(), client_address)


# def main():
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
#         server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
#         print(f"Server started at {SERVER_ADDRESS}:{SERVER_PORT}")
#
#         while True:
#             data, client_address = server_socket.recvfrom(1024)
#             data = data.decode()
#             response = handle_rerquest(data)
#             server_socket.sendto(response.encode(), client_address)
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # server_socket.bind(('', SERVER_PORT))
    #
    # print("Mail Server (UDP) đang khởi chạy...")
    #
    # while True:
    #     # Nhận yêu cầu từ client
    #     data, client_address = server_socket.recvfrom(1024)
    #     client_request = data.decode()
    #     print(f"Received: {client_request}")
    #
    #     request_parts = client_request.split(" ", 3)
    #     command = request_parts[0]
    #
    #     if command == "CREATE_ACCOUNT":
    #         create_account(request_parts[1], request_parts[2], client_address, server_socket)
    #     elif command == "LOGIN":
    #         login(request_parts[1], request_parts[2], client_address, server_socket)
    #     else:
    #         print(f"Không tìm thấy lệnh: {command}")


# if __name__ == "__main__":
#     main()
