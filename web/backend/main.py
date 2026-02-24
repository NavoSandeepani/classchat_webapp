from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected users
clients = {}


# Broadcast function (send to all users)
async def broadcast(message):
    for user in clients:
        await clients[user].send_text(json.dumps(message))


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):

    await websocket.accept()

    # Check duplicate username
    if username in clients:
        await websocket.send_text(json.dumps({
            "status": "error",
            "message": "Username already taken"
        }))
        await websocket.close()
        return

    # Store user
    clients[username] = websocket

    # Notify everyone that user joined
    await broadcast({
        "status": "join",
        "username": username,
        "online_users": list(clients.keys())
    })

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            sender = message["sender"]
            receiver = message["receiver"]
            text = message["text"]

            message["timestamp"] = datetime.now().strftime("%H:%M")

            # If receiver exists
            if receiver in clients:
                await clients[receiver].send_text(json.dumps(message))
                await websocket.send_text(json.dumps(message))
            else:
                await websocket.send_text(json.dumps({
                    "status": "error",
                    "message": "User not found"
                }))

    except WebSocketDisconnect:
        del clients[username]

        # Notify everyone user left
        await broadcast({
            
            "status": "leave",
            "username": username,
            "online_users": list(clients.keys())
        })