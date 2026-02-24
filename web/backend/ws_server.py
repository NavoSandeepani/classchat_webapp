import asyncio
import websockets
import json
from datetime import datetime
import uuid

connected_users = {}
user_images = {}

async def handler(websocket):
    username = None
    try:
        message = await websocket.recv()
        data = json.loads(message)

        if data["type"] == "join":
            username = data["username"]
            image = data["image"]

            if username in connected_users:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Username already taken"
                }))
                return

            connected_users[username] = websocket
            user_images[username] = image

            print(f"{username} connected")

            await websocket.send(json.dumps({
                "type": "join_success"
            }))

            await broadcast_users()

        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "typing":
                await broadcast({
                    "type": "typing",
                    "username": username
                }, exclude=username)
            
            if data["type"] == "join":
                connected_users[username] = websocket
                user_images[username] = data["image"]

            if data["type"] == "stop_typing":
                await broadcast({
                    "type": "stop_typing"
                })
            if data["type"] == "message":
                current_time = datetime.now().strftime("%H:%M")

            if data["type"] == "message":

                current_time = datetime.now().strftime("%H:%M")

                message_payload = {
                    "type": "message",
                    "id": str(uuid.uuid4()),
                    "sender": username,
                    "text": data["text"],
                    "image": user_images.get(username, ""),
                    "time": current_time,
                    "replyTo": data.get("replyTo"),
                    "privateTo": data.get("privateTo")
                }

                # 🔥 PRIVATE MESSAGE
                if data.get("privateTo"):
                    target = data["privateTo"]

                    # send to sender
                    await connected_users[username].send(json.dumps(message_payload))

                    # send to target
                    if target in connected_users:
                        await connected_users[target].send(json.dumps(message_payload))

                else:
                    # PUBLIC MESSAGE
                    await broadcast(message_payload)      
            

    except Exception as e:
        print("Error:", e)

    finally:
        if username and username in connected_users:
            del connected_users[username]
            del user_images[username]
            print(f"{username} disconnected")
            await broadcast_users()


async def broadcast_users():
    users = [
        {"username": u, "image": user_images[u]}
        for u in connected_users
    ]

    message = json.dumps({
        "type": "user_list",
        "users": users
    })

    for ws in connected_users.values():
        await ws.send(message)


async def broadcast(data, exclude=None):
    message = json.dumps(data)

    for user, ws in connected_users.items():
        if user != exclude:
            await ws.send(message)


async def main():
    async with websockets.serve(
        handler,
        "0.0.0.0",
        8765,
        max_size=10_000_000  # 10MB limit
):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())