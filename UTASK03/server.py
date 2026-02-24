import socket
import select
import json
from datetime import datetime

HOST = '127.0.0.1'
PORT = 5002

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("ClassChat Server is running...")

sockets_list = [server]
clients = {}  # username -> socket


def broadcast(message, exclude_socket=None):
    for user, sock in clients.items():
        if sock != exclude_socket:
            sock.send(json.dumps(message).encode())


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        # 🔹 New connection
        if notified_socket == server:
            client_socket, client_address = server.accept()
            username = client_socket.recv(1024).decode()

            # Duplicate username check
            if username in clients:
                error_msg = {
                    "status": "error",
                    "message": "Username already taken."
                }
                client_socket.send(json.dumps(error_msg).encode())
                client_socket.close()
                print(f"Rejected duplicate username: {username}")
            else:
                sockets_list.append(client_socket)
                clients[username] = client_socket

                print(f"{username} connected from {client_address}")

                # Join notification
                join_msg = {
                    "status": "info",
                    "message": f"{username} joined the chat."
                }
                broadcast(join_msg)

        # 🔹 Existing client message
        else:
            try:
                message = notified_socket.recv(1024)

                if not message:
                    # Handle disconnect
                    for user, sock in list(clients.items()):
                        if sock == notified_socket:
                            print(f"{user} disconnected")
                            del clients[user]

                            leave_msg = {
                                "status": "info",
                                "message": f"{user} left the chat."
                            }
                            broadcast(leave_msg)
                            break

                    sockets_list.remove(notified_socket)
                    notified_socket.close()
                    continue

                data = json.loads(message.decode())

                sender = data["sender"]
                receiver = data["receiver"]
                text = data["text"]

                # 🔹 Online users command
                if text.strip() == "/users":
                    user_list = ", ".join(clients.keys())
                    response = {
                        "status": "info",
                        "message": f"Online users: {user_list}"
                    }
                    notified_socket.send(json.dumps(response).encode())
                    continue

                print(f"{sender} → {receiver}: {text}")

                # Add timestamp
                data["timestamp"] = datetime.now().strftime("%H:%M:%S")

                # Forward message
                if receiver in clients:
                    clients[receiver].send(json.dumps(data).encode())

                    # Delivery confirmation
                    confirm = {
                        "status": "info",
                        "message": "Message delivered successfully."
                    }
                    notified_socket.send(json.dumps(confirm).encode())
                else:
                    error_msg = {
                        "status": "error",
                        "message": f"User {receiver} not found."
                    }
                    notified_socket.send(json.dumps(error_msg).encode())

            except:
                sockets_list.remove(notified_socket)
                notified_socket.close()

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        notified_socket.close()
