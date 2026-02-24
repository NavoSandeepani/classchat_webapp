import socket

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

ack = client.recv(1024)
print("server: " ,ack.decode())

print("Connected to server.")

while True:
    message = input("You: ")
    client.send(message.encode())
    
    data = client.recv(1024)
    print("Server:", data.decode())
