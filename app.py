import streamlit as st 
import time
import binascii
import base64
# from flask import Flask, jsonify
from bson import ObjectId
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

from services.components.users import UserIngestion
from services.components.notes import NoteIngestion

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
    note_ingestion = NoteIngestion(client)
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
        
