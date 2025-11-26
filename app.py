import streamlit as st 
import time
import binascii
import base64
from bson import ObjectId
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

from services.components.users import UserIngestion
from services.components.notes import NoteIngestion
from services.components.vault import VaultIngestion
from services.components.file import FileIngestion

# import os 
# from dotenv import load_dotenv
# load_dotenv()

# Connection to MongoDB
# from pymongo import MongoClient
# uri = os.getenv("MONGODB_URI")
# client = MongoClient(uri)

# For experiment purposes, using a local MongoDB instance
client = "mongodb://localhost:27017/"

user_ingestion = UserIngestion(client=client)
note_ingestion = NoteIngestion(client=client)
vault_ingestion = VaultIngestion(client=client)
file_ingestion = FileIngestion(client=client)

# Read the master key
with open("master.key", "r") as f:
    master_key = f.read()
    
# -------------------------------
# PAGE SETUP
# -------------------------------
st.set_page_config(page_title="CryptoLab", page_icon="🔐", layout="centered")

st.title("🔐 CryptoLab")
st.write("""
Welcome to **CryptoLab** — a mini lab to explore and test:
- Password hashing (bcrypt)
- RSA keypair generation
- Encryption of metadata
- Secure storage in MongoDB
""")

st.divider()

# ---------------------------
# USER CREATION SECTION
# ---------------------------
st.subheader("🧩 Create New User")

username = st.text_input("Enter a username", key="create_user")
password = st.text_input("Enter a password", type="password", key="create_pass")

if st.button("Create User"):
    if not username or not password:
        st.warning("Please enter both username and password.")
    else:
        doc = user_ingestion.collection.find_one({"username": username})

        if doc:
            st.error("❌ User already exists!")
        else:
            result = user_ingestion.create_user(username, password)
            if result == "User created successfully!":
                st.success("✅ User created successfully!")
            else:
                st.error("⚠️ Failed to create user. Try again.")

st.divider()

# -------------------------------
# LOGIN SECTION
# -------------------------------
st.subheader("🔑 Verify User Login")

username_login = st.text_input("Username (for login)", key="login_user")
password_attempt = st.text_input("Password", type="password", key="login_pass")

if st.button("Verify Password"):
    if not username_login or not password_attempt:
        st.warning("Please enter both username and password.")
    else:
        doc = user_ingestion.collection.find_one({"username": username_login})

        if not doc:
            st.error("🚫 User not found!")
        else:
            if user_ingestion.verify_password(username_login, password_attempt):
                st.success("✅ Password is correct. Access granted!")
                
                # ---- Decrypt private key & DEK ----
                private_pem_encrypted = doc["private_key_pem_encrypted"]
                private_key = serialization.load_pem_private_key(
                    private_pem_encrypted.encode('utf-8'),
                    password=master_key.encode('utf-8')
                )

                encrypted_user_dek_hex = doc["encrypted_user_dek"]
                encrypted_bytes = binascii.unhexlify(encrypted_user_dek_hex)

                user_dek_base64 = private_key.decrypt(
                    encrypted_bytes,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode('utf-8')

                dek_bytes = base64.urlsafe_b64decode(user_dek_base64.encode('utf-8'))

                # ---- Store session values ----
                st.session_state["username"] = username_login
                st.session_state["user_id"] = str(doc["_id"])
                st.session_state["dek"] = dek_bytes
                
                time.sleep(2)
                st.rerun()  # <<<<<<<<<< IMPORTANT
            else:
                st.error("❌ Incorrect Password. Access denied!")

st.divider()

# -------------------------------
# NOTES SECTION
# -------------------------------
st.header("🗒️ Notes")

# Initialize editing state
if "editing_note" not in st.session_state:
    st.session_state["editing_note"] = None

# ensure user is logged in
if 'dek' not in st.session_state:
    st.info("Login to view and manage your notes.")
else:
    dek = st.session_state['dek']
    user_id = st.session_state['user_id']  # str of ObjectId

    # show existing notes
    notes_list = note_ingestion.fetch_notes(owner_id=user_id)

    st.subheader("Your notes")
    if notes_list:
        for note_meta in notes_list:
            with st.expander(f"Note • {note_meta['created_at']}"):
                if st.button(f"View ⤵️", key=f"view-{note_meta['_id']}"):
                    try:
                        plaintext = note_ingestion.decrypt_note_with_dek(
                            dek=dek,
                            ciphertext_b64=note_meta['encrypted_content'],
                            nonce_b64=note_meta['nonce']
                        )
                        st.write(plaintext)
                    except Exception as e:
                        st.error(f"Decrypt failed: {e}")

                if st.button(f"Delete 🗑️", key=f"del-{note_meta['_id']}"):
                    deleted = note_ingestion.delete_note(note_meta['_id'])
                    if deleted:
                        st.success("Deleted.")
                        st.rerun()
                    else:
                        st.error("Delete failed.")

                # update flow
                # Edit button
                if st.button(f"Edit ✏️", key=f"edit-{note_meta['_id']}"):
                    st.session_state["editing_note"] = note_meta["_id"]
                    st.rerun()
                
                # If this note is currently being edited
                if st.session_state["editing_note"] == note_meta["_id"]:
                    existing_plain = note_ingestion.decrypt_note_with_dek(
                        dek=dek,
                        ciphertext_b64=note_meta['encrypted_content'],
                        nonce_b64=note_meta['nonce']
                    )

                    st.write("**Editing:**")
                    new_text = st.text_area("Edit note text", value=existing_plain, key=f"text-{note_meta['_id']}")

                    if st.button("Save Changes", key=f"save-{note_meta['_id']}"):
                        enc = note_ingestion.encrypt_note_with_dek(dek=dek, plaintext=new_text)

                        note_ingestion.update_note(
                            note_id=note_meta['_id'],
                            encrypted_content=enc['ciphertext'],
                            nonce=enc['nonce'],
                            sha256=enc['sha256']
                        )

                        st.success("Updated successfully!")
                        st.session_state["editing_note"] = None
                        st.rerun()

                    if st.button("Cancel", key=f"cancel-{note_meta['_id']}"):
                        st.session_state["editing_note"] = None
                        st.rerun()
    else:
        st.info("No notes yet. Add your first note below.")

    # add new note
    st.subheader("Add a new note")
    new_note_text = st.text_area("Write something...", key="new_note_text")
    if st.button("Add Note"):
        if not new_note_text:
            st.warning("Please write a note.")
        else:
            enc = note_ingestion.encrypt_note_with_dek(dek=dek, plaintext=new_note_text)
            inserted_id = note_ingestion.create_note(
                owner_id=ObjectId(user_id),
                encrypted_content=enc['ciphertext'],
                nonce=enc['nonce'],
                sha256=enc['sha256']
            )
            st.success("Note saved.")
            st.rerun()

# -------------------------------
# DELETE USER ACCOUNT
# -------------------------------

# Initialize username state
if "username" not in st.session_state:
    st.error("Login to delete your account.")
    st.stop()  
    
st.subheader("❌ Delete My Account")

del_pass = st.text_input("Password", type="password", key="del_pass")

if st.button("Delete My Account Permanently"):

    if not user_ingestion.verify_password(st.session_state["username"], del_pass):
        st.error("❌ Incorrect Password. Access denied!")
    else:    
        user_id = st.session_state["user_id"]

        # 1) Delete user's notes
        note_ingestion.collection.delete_many({"owner_id": ObjectId(user_id)})

        # 2) Delete user
        user_ingestion.collection.delete_one({"_id": ObjectId(user_id)})

        # 3) Clear session and refresh
        st.session_state.clear()

        st.success("Your account and all notes were deleted permanently.")
        
        time.sleep(1)
        st.rerun()

st.divider()

# -------------------------------
# VAULT SECTION
# -------------------------------
st.subheader("🔑 Vault")

# Initialize editing state
if "editing_password" not in st.session_state:
    st.session_state["editing_password"] = None

# Ensure user is looged in 
if 'dek' not in st.session_state:
    st.info("Login to view and manage your vault.")
else:
    dek = st.session_state['dek']
    user_id = st.session_state['user_id']  # str of ObjectId
    
    # ---- SERVICE DROPDOWN ----
    services = vault_ingestion.fetch_services(owner_id=user_id)

    if services:
        service = st.selectbox("Select a service:", services, key="service", placeholder='Service')
    else:
        st.info("No saved passwords yet.")
        service = None
    
    # ---- FETCH PASSWORDS ----
    password_list = []
    if service:
        password_list = vault_ingestion.fetch_passwords_by_service(
            owner_id=user_id,
            service=service  
        )   

    if password_list:
        for password in password_list:
                        
            # Make the view, update, delete button horizontal
            col1, col2, col3 = st.columns(3)
            
            # View button
            with col1:
                if st.button(f"View ⤵️", key=f"view-{password['_id']}"):
                    try:
                        plaintext = vault_ingestion.decrypt_password_with_dek(
                            dek=dek,
                            password_encrypted_b64=password['password_encrypted'],
                            nonce_64=password['nonce']
                        )
                        st.write('Service:',password['service'])
                        st.write('Password:', plaintext)
                        st.write('URL:', password['url'])
                    except Exception as e:
                        st.error(f"Decrypt failed: {e}")
            
            # Update button
            with col2:
                if st.button(f"Edit ✏️", key=f"edit-{password['_id']}"):
                    st.session_state["editing_password"] = password["_id"]
                    st.rerun()
                    
                # If this note is currently being edited
                if st.session_state["editing_password"] == password["_id"]:
                    existing_plain = vault_ingestion.decrypt_password_with_dek(
                        dek=dek,
                        password_encrypted_b64=password['password_encrypted'],
                        nonce_64=password['nonce']
                    )

                    st.write("**Editing:**")
                    new_password = st.text_input("Edit password", value=existing_plain, key=f"text-{password['_id']}")

                    if st.button("Save Changes", key=f"save-{password['_id']}"):
                        enc = vault_ingestion.encrypt_password_with_dek(dek=dek, password=new_password)

                        vault_ingestion.update_password_entry(
                            service=password['service'],
                            encrypted_content=enc['password_encrypted'],
                            nonce=enc['nonce']
                        )

                        st.success("Updated successfully!")
                        st.session_state["editing_password"] = None
                        st.rerun()

                    if st.button("Cancel", key=f"cancel-{password['_id']}"):
                        st.session_state["editing_password"] = None
                        st.rerun()
                
            # Delete button
            with col3:
                if st.button(f"Delete 🗑️", key=f"del-{password['_id']}"):
                    deleted = vault_ingestion.delete_password_entry(password['service'])
                    if deleted:
                        st.success("Deleted.")
                        st.rerun()
                    else:
                        st.error("Delete failed.")
    else:
        st.info("No passwords yet. Add your first password below.")

    # add new password
    st.subheader("Add a new password")
    
    new_service = st.text_input("Service", key="new_service")
    url = st.text_input("URL", key="url")
    new_password = st.text_input("Password", type="password", key="new_password")
        
    if new_password:
        strength = vault_ingestion.check_password_strength(new_password)
        st.write(f"Strength Score: {strength['score']}")
        st.write(strength['feedback'])
    
    if st.button("Add Password"):
        if not new_service or not url or not new_password:
            st.warning("Please fill in all fields.")
        else:
            existing = vault_ingestion.collection.find_one({
                "owner_id": ObjectId(user_id),
                "service": new_service
            })
            if existing:
                st.error("Service already exists!")
                st.stop()
            else:
                # Only allow strong passwords
                if not strength['good_password']:
                    st.warning("Password is not strong enough.")
                else:
                    enc = vault_ingestion.encrypt_password_with_dek(dek=dek, password=new_password)
                    inserted_id = vault_ingestion.create_password_entry(
                        owner_id=ObjectId(user_id),
                        service=new_service,
                        username=st.session_state['username'],
                        url=url,
                        password_encrypted=enc['password_encrypted'],
                        nonce=enc['nonce']
                    )
                    st.success("Password saved.")
                    st.rerun()

st.divider()
# -------------------------------
# FILE SECTION
# -------------------------------
st.header("📁 Files")

# File uploader of whatever type(all)
uploaded_file = st.file_uploader(
    "Upload a file",
    type=None,
    key="file_uploader",
    help="Upload any file for storage."
)

if st.button("Upload file"):
    st.session_state.pop("uploaded_file_processed", None)
    st.rerun()

if uploaded_file is not None and "uploaded_file_processed" not in st.session_state:
    
    st.session_state["uploaded_file_processed"] = True
    
    if 'dek' not in st.session_state or "user_id" not in st.session_state:
        st.error("Login to upload files.")
        st.stop()
    else:
        dek = st.session_state['dek']
        username = st.session_state['username']
        user_id = st.session_state['user_id']
        
        data = uploaded_file.read()  
            
        enc = file_ingestion.encrypt_file(
            data=data,
            dek=dek
        )

        metadata = {
            "owner_id": ObjectId(user_id),
            "original_filename": uploaded_file.name,
            "sha256": enc['sha256'],
            "encrypted": True,
            "content_type": uploaded_file.type,
            "uploaded_at": datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
        }
        
        file_id = file_ingestion.upload_to_gridfs(
            filename=f"{uploaded_file.name[:7]}.enc", 
            encrypted_bytes=enc['encrypted_bytes'], 
            metadata=metadata
        )
        st.success(f"File uploaded with ID: {file_id}")
        
st.subheader("Your uploaded files")

files = file_ingestion.get_files_list(owner_id=st.session_state["user_id"])

for file in files:
    with st.expander(file["filename"]):
        st.write("Uploaded:", file["metadata"]["uploaded_at"])
        file_id = file["_id"]

        col1, col2 = st.columns(2)
        
    with col1:
        if st.button("Decrypt & Prepare Download", key=f"dl-{file_id}"):
            try:
                encrypted_bytes = file_ingestion.download_from_gridfs(file_id)
                dek = st.session_state["dek"]
                decrypted_data = file_ingestion.decrypt_file(encrypted_bytes, dek)

                # Integrity check
                if not file_ingestion.integrity_check(decrypted_data, file["metadata"]["sha256"]):
                    st.error("Integrity check failed — file may be corrupted.")
                    st.info("Delete this file...")
                else:
                    st.download_button(
                        label="Download File",
                        data=decrypted_data,
                        file_name=file["metadata"]["original_filename"],
                        mime=file["metadata"]["content_type"]
                    )
            except Exception as e:
                st.error(f"Download failed: {e}")

        with col2:
            if st.button(f"Delete", key=f"del-{file_id}"):
                file_ingestion.delete_from_gridfs(file_id)
                st.success("Deleted!")
                st.rerun()
                
st.divider()
# -------------------------------
# OPTIONAL: DATABASE SUMMARY
# -------------------------------
if st.checkbox("Show stored users (for testing only)"):
    user_ingestion = UserIngestion(client=client)
    users = list(user_ingestion.collection.find({}, {"_id": 0, "username": 1, "public_key_pem": 1}))
    
    if users:
        st.write("🧾 **Registered Users:**")
        for user in users:
            st.write(f"• **{user['username']}**")
    else:
        st.info("No users found.")
        
