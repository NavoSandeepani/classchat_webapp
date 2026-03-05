import socket
import threading
import json
import sys

HOST = '10.102.14.236'
PORT = 5002

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

username = input("Enter your username: ")
client.send(username.encode())

# 🔹 Check duplicate username response
response = client.recv(1024)
try:
    data = json.loads(response.decode())
    if data["status"] == "error":
        print("Error:", data["message"])
        client.close()
        sys.exit()
except:
    pass

print("Connected to ClassChat!")

# 🔹 Receive messages thread
def receive_messages():
    while True:
        try:
            message = client.recv(1024)
            if not message:
                print("Disconnected from server")
                break

            data = json.loads(message.decode())

            # Info message
            if data.get("status") == "info":
                print(f"\n[INFO]: {data['message']}")

            # Error message
            elif data.get("status") == "error":
                print(f"\n[ERROR]: {data['message']}")

            # Normal message
            else:
                timestamp = data.get("timestamp", "")
                reply = data.get("reply_to")
                forwarded = data.get("forwarded_from")

                print()

                if forwarded:
                    print(f"[Forwarded from {forwarded}]")

                if reply:
                    print(f"[Reply to: {reply}]")

                print(f"[{timestamp}] {data['sender']} → You: {data['text']}")

        except:
            break


thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()


# 🔹 Sending messages
while True:
    receiver = input("\nSend to: ")

    # Special command support
    if receiver.strip() == "":
        continue

    print("1) Normal Message")
    print("2) Reply")
    print("3) Forward")
    choice = input("Choose option (1/2/3): ")

    text = input("Message: ")

    message = {
        "status": "1",
        "sender": username,
        "receiver": receiver,
        "text": text
    }

    # Reply feature
    if choice == "2":
        reply_text = input("Replying to message: ")
        message["reply_to"] = reply_text

    # Forward feature
    elif choice == "3":
        original_sender = input("Forwarded from (original sender name): ")
        message["forwarded_from"] = original_sender

    try:
        client.send(json.dumps(message).encode())
    except:
        print("Failed to send message.")
        break
