import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Symmetric Encryption using AES-GCM
def aes_ed(message):
    key = secrets.token_bytes(32)  # AES-256 key
    nonce = secrets.token_bytes(12)  # Recommended nonce size for AES-GCM
    aes = AESGCM(key)
    
    ciphertext = nonce + aes.encrypt(nonce, message.encode(), None)
    plaintext = aes.decrypt(ciphertext[:12], ciphertext[12:], None)
    
    return key.hex(), ciphertext.hex(), plaintext.decode()

# Assymmetric Encryption using RSA
def rsa_ed(message):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    
    ciphertext = public_key.encrypt(
        message.encode(),
        # The hash algorithm to use with OAEP(Optimal Asymmetric Encryption Padding)
        padding.OAEP(
            # The mask generation function(mgf) to use
            mgf = padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf = padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext.hex(), plaintext.decode()
    

if __name__ == "__main__":
    print("AES Encryption/Decryption:")
    key, ciphertext, plaintext = aes_ed("Hello, World!")
    print(f"AES Key: {key}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Decrypted Plaintext: {plaintext}")
    
    print("\nRSA Encryption/Decryption:")
    ciphertext, plaintext = rsa_ed("Hello, World!")
    print(f"Ciphertext: {ciphertext}")
    print(f"Decrypted Plaintext: {plaintext}")
    
