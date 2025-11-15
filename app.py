import streamlit as st 
from flask import Flask, jsonify
from pymongo import MongoClient
from services.components.users import UserIngestion

# import os 
# from dotenv import load_dotenv
# load_dotenv()

# Connection to MongoDB
# uri = os.getenv("MONGODB_URI")
# client = MongoClient(uri)

# For experiment purposes, using a local MongoDB instance
client = "mongodb://localhost:27017/"

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

# -------------------------------
# USER CREATION SECTION
# -------------------------------
st.subheader("🧩 Create New User")

username = st.text_input("Enter a username", key="create_user")
password = st.text_input("Enter a password", type="password", key="create_pass")

if st.button("Create User"):
    if not username or not password:
        st.warning("Please enter both username and password.")
    else:
        user_ingestion = UserIngestion(client=client)
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
        user_ingestion = UserIngestion(client=client)
        doc = user_ingestion.collection.find_one({"username": username_login})

        if not doc:
            st.error("🚫 User not found!")
        else:
            if user_ingestion.verify_password(username_login, password_attempt):
                st.success("✅ Password is correct. Access granted!")
            else:
                st.error("❌ Incorrect Password. Access denied!")

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
        st.info("No users found yet.")
