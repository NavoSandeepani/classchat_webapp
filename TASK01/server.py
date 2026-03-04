import socket

HOST = '127.0.0.1' #localhost IP adress(server run on your own computer)
PORT = 5000 #prt nu.door number where communication happen

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#AF_INET-IPv4 address format,SOCK_STREAM-TCP protocol
server.bind((HOST, PORT))#attach to server
server.listen(1)#start to incomming connection,1-1client at a time

print("Server is listening...")#show the server is ready

conn, addr = server.accept()#server wait until client connect,conn-new socket for communication with that client,addre-client add,port
print(f"Connected by {addr}")

conn.send("Connected Succesfully to server." .encode())

while True: #the server ll keep connection end
    data = conn.recv(1024)# receive dta from client
    if not data:
        break
    
    message = data.decode()#binary data convert readable
    print("Client:", message)

    # Exit condition
    if message.lower() == "exit":
        print("Client disconnected.")
        break
    
    reply = input("Server reply: ")
    conn.send(reply.encode())

    if reply.lower() == "exit":
        print("Server closing connection.")
        break

conn.close()
server.close()

print("Connection closed.")