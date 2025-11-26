import os 
import base64
from pymongo import MongoClient
import gridfs
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import binascii
from bson import ObjectId
from services.constant.collection_pipeline import DATABASE_NAME
from datetime import datetime


class FileIngestion:
    def __init__(self, client):
        self.client = MongoClient(client)
        self.database = self.client[DATABASE_NAME]
        self.fs = gridfs.GridFS(self.database)

    def encrypt_file(self, data, dek: bytes) -> dict:
        """
        Encrypts a file using AES-GCM with a given DEK.

        Parameters:
            input_path (str): The path to the file to be encrypted.
            dek (bytes): The raw bytes of the Data Encryption Key (DEK).

        Returns:
            dict: A dictionary containing the encrypted file data and its SHA-256 hash.
        """
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if isinstance(dek, str):
            dek = base64.b64decode(dek)
        
        aes = AESGCM(dek)
        nonce = os.urandom(12)

        encrypted_data = aes.encrypt(nonce, data, associated_data=None)
        sha_digest = hashlib.sha256(data).hexdigest()
        encrypted_bytes = nonce + encrypted_data
        
        return {
            "encrypted_bytes": encrypted_bytes,
            "sha256": sha_digest
        }
            
        
    def decrypt_file(self, encrypted_bytes: bytes, dek: bytes) -> bytes:
        '''
        Decrypt a file using AES-GCM with a given DEK.

        Parameters:
            encrypted_bytes (bytes): The encrypted file data.
            dek (bytes): The raw bytes of the Data Encryption Key (DEK).

        Returns:
            bytes: The decrypted file data.

        Raises:
            Exception: If the nonce size is invalid or the encrypted data size is not a multiple of 16.
        '''
        if isinstance(dek, str):
            dek = base64.b64decode(dek)
            
        aes = AESGCM(dek)
        nonce = encrypted_bytes[:12]
        encrypted_data = encrypted_bytes[12:]
        
        if len(nonce) != 12:
            raise Exception("Invalid nonce size")

        decrypted_data = aes.decrypt(nonce, encrypted_data, None)

        # Later in the app code, I'll save the decrypted data to a file
        return decrypted_data

    def integrity_check(self, decrypted_data: bytes, sha256: str) -> bool:
        sha_digest = hashlib.sha256(decrypted_data).hexdigest()
        return sha_digest == sha256
    
    def get_files_list(self, owner_id: ObjectId):
        files = self.database.fs.files.find({"metadata.owner_id": ObjectId(owner_id)}).sort("uploadDate", -1)
        return list(files)
    
    
    def upload_to_gridfs(self, filename, encrypted_bytes: bytes, metadata: dict = None):
        
        file_id = self.fs.put(encrypted_bytes, filename=filename, metadata=metadata or {})
        return file_id
    
    def download_from_gridfs(self, file_id):
        data = self.fs.get(file_id).read()
        return data
    
    def delete_from_gridfs(self, file_id):
        self.fs.delete(file_id)
        return True
    