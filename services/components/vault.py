import os 
import base64
from pymongo import MongoClient
import hashlib
from zxcvbn import zxcvbn
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import binascii
from bson import ObjectId
from services.constant.collection_pipeline import (
    DATABASE_NAME,
	COLLECTION_VAULT
)
from datetime import datetime

class VaultIngestion:
    def __init__(self, client):
        self.client = MongoClient(client)
        self.database = self.client[DATABASE_NAME]
        self.collection = self.database[COLLECTION_VAULT]
        
    def encrypt_password_with_dek(self, dek: bytes, password: str) -> dict:
        """
        dek: raw bytes (32 bytes for AES-256)
        password: string
        returns dict: {ciphertext, nonce, sha256}
        """
        if isinstance(dek, str):
            # defensive: if someone passes base64 string accidentally
            dek = base64.b64decode(dek)
        
        aesgcm = AESGCM(dek)
        nonce = os.urandom(12) # 12 bytes * 8 bits/byte = 96-bit nonce for GCM
        password_encrypted = aesgcm.encrypt(nonce, password.encode('utf-8'), associated_data=None)
        
        return {
            "password_encrypted": base64.b64encode(password_encrypted).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8')
        }
        
    def decrypt_password_with_dek(self, dek: bytes, password_encrypted_b64: str, nonce_64: str) -> str:
        """
        dek: raw bytes
        password_encrypted_b64, nonce_b64: base64 strings from DB
        returns password string (raises on auth failure)
        """
        if isinstance(dek, str):
            dek = base64.b64decode(dek)
        
        aesgcm = AESGCM(dek)
        nonce = base64.b64decode(nonce_64)
        password_encrypted = base64.b64decode(password_encrypted_b64)
        password = aesgcm.decrypt(nonce, password_encrypted, associated_data=None)
        
        return password.decode('utf-8')
    
    def check_password_strength(self, password: str) -> dict:
        """
        Check the strength of a given password using the zxcvbn library.

        Args:
            password (str): The password to be evaluated.

        Returns:
            dict: A dictionary containing the strength score and feedback.
        """
        result = zxcvbn(password)
        score = result["score"]
        feedback = result["feedback"]
        
        good_password = False
        if score >= 3:
            good_password = True

        return {
            "score": score,
            "good_password": good_password,
            "feedback": feedback
        }

    def fetch_services(self, owner_id: ObjectId):
        """
        Returns a sorted list of unique services for this user.
        """
        services = self.collection.distinct(
            "service",
            {"owner_id": ObjectId(owner_id)}
        )
        return sorted(services)
        
    # -------------------
    # CRUD for passsword
    # -------------------
    def create_password_entry(self, owner_id: ObjectId, password_encrypted: str, nonce: str, service: str, username: str, url: str):
        doc = {
            "owner_id": ObjectId(owner_id),
            "username": username,
            "service": service,
            "url": url,
            "password_encrypted": password_encrypted,
            "nonce": nonce,
            "created_at": datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
        }
        res = self.collection.insert_one(doc)
        return str(res.inserted_id)

    def fetch_passwords_by_service(self, owner_id: ObjectId, service: str):
        # self.collection.find({"owner_id": ObjectId(owner_id)})
        # self.collection.find({"service": {"$regex": "gmail", "$options": "i"}})
        cursor = self.collection.find({
            "owner_id": ObjectId(owner_id),
            "service": service
        })
        notes = []
        for doc in cursor:
            notes.append({
                "_id": str(doc["_id"]),
                "owner_id": str(doc["owner_id"]),
                "username": doc["username"],
                "service": doc["service"],
                "url": doc["url"],
                "password_encrypted": doc["password_encrypted"],
                "nonce": doc["nonce"],
                "created_at": doc.get("created_at")
            })
        return notes
    
    # Why use `service` not `id`? Because service is unique for each user
    def update_password_entry(self, service: str, encrypted_content: str, nonce: str):
        doc = {
            "password_encrypted": encrypted_content,
            "nonce": nonce
        }
        res = self.collection.update_one({"service": service}, {"$set": doc})
        return res
    
    def delete_password_entry(self, service: str):
        res = self.collection.delete_one({"service": service})
        return res

