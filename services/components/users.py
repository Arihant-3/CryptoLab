import os 
import streamlit as st
import base64
from pymongo import MongoClient
import bcrypt
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import binascii
from services.constant.collection_pipeline import (
    DATABASE_NAME,
	COLLECTION_USERS
)
from datetime import datetime

# Read the master key
master_key = st.secrets["MASTER_KEY"]

class UserIngestion:
    def __init__(self, client):
        self.client = MongoClient(client)
        self.database = self.client[DATABASE_NAME]
        self.collection = self.database[COLLECTION_USERS]
    
    def generate_rsa_keypair(self):
        # Generate RSA private key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # Serialize keys to PEM (text) for storage/use
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            # Production: Encryption algorithm must be a KeySerializationEncryption instance
            encryption_algorithm=serialization.BestAvailableEncryption(master_key.encode('utf-8'))
        ).decode('utf-8')

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return private_key, public_key, private_pem, public_pem

    def encrypt_with_public(self, public_key, plaintext: str) -> str:
        ciphertext = public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # store hex or base64
        return binascii.hexlify(ciphertext).decode('utf-8')

    def decrypt_with_private(self, private_key, hex_ciphertext: str) -> str:
        ciphertext = binascii.unhexlify(hex_ciphertext)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode('utf-8')
    
    def create_user(self, username: str, password: str):
        # 1) Hash password for 
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        # 2) Generate RSA keypair for the user (for encrypting DEKs / metadata)
        priv, pub, priv_pem, pub_pem = self.generate_rsa_keypair()

        # 3) Generate a DEK for the user’s future data
        user_dek = base64.urlsafe_b64encode(os.urandom(32)).decode()
        # Encrypt that DEK using the user’s RSA public key
        encrypted_user_dek = self.encrypt_with_public(pub, user_dek)
        
        # 4) Save user record (do NOT store private_pem in the DB in production)
        doc = {
            "username": username,
            "password_hash": pwd_hash,
            "public_key_pem": pub_pem,
            "private_key_pem_encrypted": priv_pem,
            "encrypted_user_dek": encrypted_user_dek,
            "date_created": datetime.now().strftime('%m/%d/%Y %I:%M:%S %p'),
        }
        if self.collection.find_one({"username": username}):
            return "User already exists!"
        self.collection.insert_one(doc)
        return "User created successfully!"

    def verify_password(self, username: str, candidate_password: str) -> bool:
        """
        Verify a given password against a hashed password.

        Args:
            password (str): The plain text password to verify.
            hashed (str): The hashed password to compare against.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        doc = self.collection.find_one({"username": username})
        stored_hash = doc.get("password_hash")
        if bcrypt.checkpw(candidate_password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True
        else:
            return False

