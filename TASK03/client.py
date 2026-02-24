import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 5002

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

username = input("Enter your username: ")
client.send(username.encode())

print("Connected to ClassChat!")

# Receive messages thread
def receive_messages():
    while True:
        try:
            message = client.recv(1024)

            if not message:
                print("Disconnected from server")
                break

            data = json.loads(message.decode())

            if "status" in data and data["status"] == "error":
                print("Error:", data["message"])
            else:
                print(f"\n{data['sender']} → You: {data['text']}")

        except:
            break

thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()

# Sending messages
while True:
    receiver = input("Send to: ")
    text = input("Message: ")

    message = {
        "status": "1",
        "sender": username,
        "receiver": receiver,
        "text": text
    }

    client.send(json.dumps(message).encode())
