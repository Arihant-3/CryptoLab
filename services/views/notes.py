import streamlit as st 
from bson import ObjectId
from services.components.notes import NoteIngestion     

# Connection to MongoDB
uri = st.secrets["MONGO_URI"]

note_ingestion = NoteIngestion(uri)

def notes_page():
    # -------------------------------
    # NOTES SECTION
    # -------------------------------
    st.title("🗒️ Notes")
    
    # Initialize editing state
    if "editing_note" not in st.session_state:
        st.session_state["editing_note"] = None

    # ensure user is logged in
    if 'dek' not in st.session_state:
        st.info("Login to view and manage your notes.")
    else:
        dek = st.session_state['dek']
        user_id = st.session_state['user_id']  # str of ObjectId
        st.write(f"Welcome {st.session_state['username']}!")
        
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
                            st.code(plaintext, language='plaintext')
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

    st.divider()
