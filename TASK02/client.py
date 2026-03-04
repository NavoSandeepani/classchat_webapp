import socket
import threading

HOST = '10.102.14.236'
PORT = 5001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print("Connected to chat server.")
print("Type messages and press ENTER")

# Receive messages
def receive_messages():
    while True:
        try:
            message = client.recv(1024)

            if not message:
                print("Server closed connection")
                break

            print("\nMessage:", message.decode())

        except:
            break

thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()

# Send messages
while True:

    message = input()

    if message.lower() == "exit":
        print("Disconnecting...")
        client.close()
        break

    client.send(message.encode())