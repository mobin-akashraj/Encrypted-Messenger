# ================= SERVER =================
# server.py
import socket, threading, json

clients = {}

def broadcast(sender, message):
    for user, conn in clients.items():
        if user != sender:
            try:
                conn.send(json.dumps(message).encode())
            except:
                conn.close()
                del clients[user]

def handle_client(conn):
    user = json.loads(conn.recv(1024).decode())
    username = user["username"]
    clients[username] = conn
    print(f"{username} connected.")
    
    while True:
        try:
            msg = json.loads(conn.recv(4096).decode())
            broadcast(username, msg)
        except:
            print(f"{username} disconnected.")
            conn.close()
            del clients[username]
            break

s = socket.socket()
s.bind(("0.0.0.0", 5555))
s.listen()
print("Server listening on port 5555")

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


