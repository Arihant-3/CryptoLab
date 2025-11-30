import streamlit as st 
from bson import ObjectId
from datetime import datetime
from services.components.file import FileIngestion

# Connection to MongoDB
uri = st.secrets["MONGO_URI"]

file_ingestion = FileIngestion(uri)

def files_page():
    # -------------------------------
    # FILE SECTION
    # -------------------------------
    st.title("📁 Files")

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
    
    if "user_id" not in st.session_state:
        st.info("Login to view files.")
        st.stop()
        
    files = file_ingestion.get_files_list(owner_id=st.session_state["user_id"])
    st.write(f"Welcome {st.session_state['username']}!")

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