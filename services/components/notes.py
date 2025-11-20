import os 
import base64
from pymongo import MongoClient
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import binascii
from bson import ObjectId
from services.constant.collection_pipeline import (
    DATABASE_NAME,
	COLLECTION_NOTES
)
from datetime import datetime

class NoteIngestion:
    def __init__(self, client):
        self.client = MongoClient(client)
        self.database = self.client[DATABASE_NAME]
        self.collection = self.database[COLLECTION_NOTES]
    
    # Make the notes encrpyted with a DEK
    # ------------------
    # AES-GCM helpers
    # ------------------
    def encrypt_note_with_dek(self, dek: bytes, plaintext: str) -> dict:
        """
        dek: raw bytes (32 bytes for AES-256)
        plaintext: string
        returns dict: {ciphertext, nonce, sha256}
        """
        if isinstance(dek, str):
            # defensive: if someone passes base64 string accidentally
            dek = base64.b64decode(dek)

        aesgcm = AESGCM(dek)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), associated_data=None)

        sha256_digest = hashlib.sha256(plaintext.encode('utf-8')).hexdigest()

        return {
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "sha256": sha256_digest
        }

        
    # Make the notes decrpyted with a DEK
    def decrypt_note_with_dek(self, dek: bytes, ciphertext_b64: str, nonce_b64: str) -> str:
        """
        dek: raw bytes
        ciphertext_b64, nonce_b64: base64 strings from DB
        returns plaintext string (raises on auth failure)
        """
        if isinstance(dek, str):
            dek = base64.b64decode(dek)

        aesgcm = AESGCM(dek)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
        return plaintext.decode('utf-8')
    
    # ------------------
    # CRUD
    # ------------------
    def create_note(self, owner_id: ObjectId, encrypted_content: str, nonce: str, sha256: str):
        doc = {
            "owner_id": ObjectId(owner_id),
            "encrypted_content": encrypted_content,
            "nonce": nonce,
            "sha256": sha256,
            "created_at": datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
        }
        res = self.collection.insert_one(doc)
        return str(res.inserted_id)

    def fetch_notes(self, owner_id: ObjectId):
        cursor = self.collection.find({"owner_id": ObjectId(owner_id)})
        notes = []
        for doc in cursor:
            notes.append({
                "_id": str(doc["_id"]),
                "owner_id": str(doc["owner_id"]),
                "encrypted_content": doc["encrypted_content"],
                "nonce": doc["nonce"],
                "sha256": doc.get("sha256"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at")
            })
        return notes

    def update_note(self, note_id: str, encrypted_content: str, nonce: str, sha256: str):
        doc = {
            "encrypted_content": encrypted_content,
            "nonce": nonce,
            "sha256": sha256,
            "updated_at": datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
        }
        res = self.collection.update_one({"_id": ObjectId(note_id)}, {"$set": doc})
        return res
    
    def delete_note(self, note_id: str):
        res = self.collection.delete_one({"_id": ObjectId(note_id)})
        return res.deleted_count
    
    
    
    