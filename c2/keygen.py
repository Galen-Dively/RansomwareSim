from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from globals import KEYSIZE


def create_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=KEYSIZE)
    public_key = private_key.public_key()
    return private_key, public_key

# def save_keypair(private_key: rsa.RSAPrivateKey, public_key: rsa.RSAPublicKey):
#     private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
#                                             format=serialization.PrivateFormat.PKCS8,
#                                             encryption_algorithm=serialization. NoEncryption()
#                                             )
#     public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
#                                          format=serialization.PublicFormat.SubjectPublicKeyInfo
#                                         )


#     with open("private.pem", "w") as f:
#         f.write(private_pem)

#     with open("public.pem", "w") as f:
#         f.write(public_pem)
