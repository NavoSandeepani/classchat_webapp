import socket
import select

HOST = '127.0.0.1'
PORT = 5001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

server.setblocking(False)

clients = []
sockets_list = [server]

print("Server is running and waiting for connections...")

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server:
            client_socket, client_address = server.accept()
            sockets_list.append(client_socket)
            clients.append(client_socket)
            print(f"New connection from {client_address}")
        else:
            try:
                message = notified_socket.recv(1024)
                if not message:
                    sockets_list.remove(notified_socket)
                    clients.remove(notified_socket)
                    notified_socket.close()
                    continue

                print("Received:", message.decode())

                # Broadcast message to all other clients
                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(message)

            except:
                sockets_list.remove(notified_socket)
                clients.remove(notified_socket)
                notified_socket.close()

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        clients.remove(notified_socket)
        notified_socket.close()
