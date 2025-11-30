import streamlit as st
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import binascii, base64
from services.components.users import UserIngestion
from services.components.notes import NoteIngestion

# Connection to MongoDB
uri = st.secrets["MONGO_URI"]

user_ingestion = UserIngestion(uri)
note_ingestion = NoteIngestion(uri)

# Read the master key
master_key = st.secrets["MASTER_KEY"]

def new_user():
    # ---------------------------
    # USER CREATION SECTION
    # ---------------------------
    st.title("🧩 Create New User")

    with st.form("create_user_form"):
        username = st.text_input("Enter a username", key="create_user")
        password = st.text_input("Enter a password", type="password", key="create_pass")

        submitted = st.form_submit_button("Create User")

        if submitted:
            if not username or not password:
                st.warning("Please enter both username and password.")
            else:
                doc = user_ingestion.collection.find_one({"username": username})

                if doc:
                    st.error("User already exists!")
                else:
                    result = user_ingestion.create_user(username, password)
                    if result == "User created successfully!":
                        st.success("User created successfully!")
                    else:
                        st.error("Failed to create user. Try again.")

    st.divider()

def login_page():
    # -------------------------------
    # LOGIN SECTION
    # -------------------------------
    # centre the title
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h1>🔑 Login</h1></div>', unsafe_allow_html=True)
    st.divider()
    
    # Centering layout with columns
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<h2 style="text-align: center; margin-bottom: 10px;">Welcome Back</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #8b949e; margin-bottom: 30px;">Securely access your encrypted workspace</p>', unsafe_allow_html=True)

        with st.form("login_form"):
            username_login = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password_attempt = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            
            st.markdown("<br>", unsafe_allow_html=True)

            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if not username_login or not password_attempt:
                    st.warning("Please enter both username and password.")
                else:
                    doc = user_ingestion.collection.find_one({"username": username_login})

                    if not doc:
                        st.error("User not found!")
                    else:
                        if user_ingestion.verify_password(username_login, password_attempt):
                            st.success("Access granted! Decrypting services...")
                            st.info("You can now view and manage your vault, notes and files through the sidebar.")
                            # ---- Decrypt private key & DEK ----
                            try:
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
                                
                                # time.sleep(1)
                                # st.rerun()
                            except Exception as e:
                                st.error(f"Decryption failed: {e}")
                        else:
                            st.error("Incorrect Password. Access denied!")

    
