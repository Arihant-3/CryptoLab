import streamlit as st
import time
from bson import ObjectId
from services.components.users import UserIngestion
from services.components.notes import NoteIngestion
from services.components.vault import VaultIngestion
from services.components.file import FileIngestion

# Connection to MongoDB
uri = st.secrets["MONGO_URI"]

user_ingestion = UserIngestion(uri)
note_ingestion = NoteIngestion(uri)
vault_ingestion = VaultIngestion(uri)
file_ingestion = FileIngestion(uri)


def delete_user():
    # -------------------------------
    # DELETE USER ACCOUNT
    # -------------------------------
    st.title("Delete User")
    
    # Initialize username state
    if "username" not in st.session_state:
        st.info("Login to delete your account.")
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

            # 2) Delete vault
            vault_ingestion.collection.delete_many({"owner_id": ObjectId(user_id)})
            
            # 3) Delete files
            # 3) Delete files by file_id
            for file in file_ingestion.get_files_list(owner_id=ObjectId(user_id)):
                file_ingestion.delete_from_gridfs({"_id": file['_id']})
            
            # 4) Delete user
            user_ingestion.collection.delete_one({"_id": ObjectId(user_id)})

            # Clear session and refresh
            st.session_state.clear()

            st.success("Your account and all notes were deleted permanently.")
            
            time.sleep(1)
            st.rerun()

    st.divider()