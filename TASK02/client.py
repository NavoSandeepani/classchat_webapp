import socket
import threading

HOST = '127.0.0.1'
PORT = 5001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print("Connected to chat server.")
print("You can start typing messages.")

# Thread to receive messages
def receive_messages():
    while True:
        try:
            message = client.recv(1024)
            if not message:
                print("Disconnected from server")
                break
            print("\nMessage:", message.decode())
        except:
            break

# Start receiving thread
thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()

# Main thread handles sending
while True:
    message = input()
    client.send(message.encode())
