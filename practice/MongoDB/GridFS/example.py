from pymongo import MongoClient
import gridfs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import datetime

# ============ MongoDB Connection ============
client = MongoClient("mongodb://localhost:27017")
db = client["Test_encrypted_files_db"]
fs = gridfs.GridFS(db)

example_metadata = {
    "filename": "secret.pdf",
    "owner": "Arihant",
    "uploaded_at": datetime.datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
}

# ============ Encryption ============
def encrypt_file(input_path, key):
    aes = AESGCM(key)
    iv = os.urandom(12)

    with open(input_path, "rb") as f:
        data = f.read()

    encrypted_data = aes.encrypt(iv, data, None)
    return iv + encrypted_data     # IV + TAG + CIPHERTEXT stored together

# ============ Decryption ============
def decrypt_file(encrypted_bytes, key, output_path):
    aes = AESGCM(key)

    iv = encrypted_bytes[:12]
    encrypted_content = encrypted_bytes[12:]

    decrypted_data = aes.decrypt(iv, encrypted_content, None)

    with open(output_path, "wb") as f:
        f.write(decrypted_data)


# ============ Upload to MongoDB GridFS ============
def upload_to_gridfs(filename, encrypted_bytes):
    # Adding metadata
    file_id = fs.put(encrypted_bytes, filename=filename, meta456585data=example_metadata)
    print("File uploaded with ID:", file_id)
    return file_id


# ============ Download from MongoDB GridFS ============
def download_from_gridfs(file_id):
    data = fs.get(file_id).read()
    return data


# ======= Example Usage =======
if __name__ == "__main__":
    key = AESGCM.generate_key(bit_length=256)  # Example key

    encrypted_bytes = encrypt_file("secret.pdf", key)

    # Upload encrypted file to MongoDB
    file_id = upload_to_gridfs("secret.pdf.enc", encrypted_bytes)

    # Download encrypted file from MongoDB
    downloaded = download_from_gridfs(file_id)

    # Decrypt it
    decrypt_file(downloaded, key, "secret_decrypted.pdf")

    print("Done! File encrypted, uploaded, downloaded, and decrypted.")
