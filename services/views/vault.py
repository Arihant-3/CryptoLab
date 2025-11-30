import streamlit as st 
from bson import ObjectId
from services.components.vault import VaultIngestion

# Connection to MongoDB
uri = st.secrets["MONGO_URI"]

vault_ingestion = VaultIngestion(uri)

def vault_page():
    # -------------------------------
    # VAULT SECTION
    # -------------------------------
    st.title("🔑 Vault")

    # Initialize editing state
    if "editing_password" not in st.session_state:
        st.session_state["editing_password"] = None

    # Ensure user is looged in 
    if 'dek' not in st.session_state:
        st.info("Login to view and manage your vault.")
    else:
        dek = st.session_state['dek']
        user_id = st.session_state['user_id']  # str of ObjectId
        st.write(f"Welcome {st.session_state['username']}!")
        
        # ---- SERVICE DROPDOWN ----
        services = vault_ingestion.fetch_services(owner_id=user_id)

        if services:
            service = st.selectbox("Select a service:", services, key="service", placeholder='Service')
        else:
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
                col1, col2, col3 = st.columns([1.5, 1.5, 1.2])
                
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
                            st.write('Password:')
                            st.code(plaintext, language='plaintext')
                            st.write('URL:')
                            st.code(password['url'], language='plaintext')
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
