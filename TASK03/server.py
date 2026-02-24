import socket
import select
import json

HOST = '127.0.0.1'
PORT = 5002

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("ClassChat Server is running...")

sockets_list = [server]
clients = {}  # username -> socket

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        # New connection
        if notified_socket == server:
            client_socket, client_address = server.accept()
            sockets_list.append(client_socket)

            # Receive username safely
            username = client_socket.recv(1024).decode()

            if username:
                clients[username] = client_socket
                print(f"{username} connected from {client_address}")
            else:
                sockets_list.remove(client_socket)
                client_socket.close()

        # Existing client sending message
        else:
            try:
                message = notified_socket.recv(1024)

                if not message:
                    # Client disconnected
                    for user, sock in list(clients.items()):
                        if sock == notified_socket:
                            print(f"{user} disconnected")
                            del clients[user]
                            break

                    sockets_list.remove(notified_socket)
                    notified_socket.close()
                    continue

                data = json.loads(message.decode())

                sender = data["sender"]
                receiver = data["receiver"]
                text = data["text"]

                print(f"{sender} → {receiver}: {text}")

                # Forward message if receiver exists
                if receiver in clients:
                    clients[receiver].send(message)
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
