import streamlit as st
from services.views.user import new_user, login_page

st.set_page_config(page_title="CryptoLab", page_icon="🔐", layout="wide")

# Initial state
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Sidebar
choice = st.sidebar.radio(
    "Navigation",
    ["Home", "Notes", "Vault", "Files"],
    key="sidebar_choice",
    width='stretch'
)

# Routing
if st.session_state.page != choice:
    if choice == "Home":
        if st.session_state.page == "New User":
            new_user()
            
            if st.button("Home"):
                st.session_state.page = "Home"
                st.rerun()
            
        elif st.session_state.page == "Login":
            login_page()
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Setting", width='stretch'):
                    st.session_state.page = "Settings"
            with col2:
                if st.button("Home", width='stretch'):
                    st.session_state.page = "Home"
                    st.rerun()
                    
        else:
            st.session_state.page = "Home"
        
    else:
        st.session_state.page = choice
        st.rerun()   
    
# Pages
if st.session_state.page == "Home":
    st.markdown("""
    <div style="text-align:center; padding-top:20px; padding-bottom:10px;">
        <h1 style="font-size:42px; margin-bottom:5px;">🔐 CryptoLab</h1>
        <p style="font-size:18px; color:#8b949e;">
            A fully client-side encrypted workspace for <b>Notes</b>, <b>Password Vault</b>, and <b>File Storage</b>.
            <br>No plaintext ever touches the database ( only encrypted blobs ).
        </p>
    </div>
    """, unsafe_allow_html=True)
        
    if st.button("Create New User", width='stretch'):
        st.session_state.page = "New User"
        st.rerun()

    if st.button("Login", width='stretch'):
        st.session_state.page = "Login"
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    ### 🔏 Why CryptoLab?

    - AES-256 + RSA Hybrid Encryption  
    - Your DEK is decrypted only on your device  
    - MongoDB stores <b>ciphertext only</b> (zero plaintext)  
    - Includes Notes, Password Vault, and File Encryption  
    - Educational, transparent, and easy to audit  

    """)

    st.markdown("---")

    # ------------------------  
    # PLACEHOLDER: DB Screenshot
    # ------------------------
    st.subheader("📦 How Your Data Looks in the Database")

    st.markdown("""
    Below is a sanitized screenshot placeholder showing what your data looks like in MongoDB.
    Notice how everything is encrypted - no readable text is stored anywhere.
    """)
    user_image = "assets/screenshot/image_user.png"
    note_image = "assets/screenshot/image_notes.png"
    vault_image = "assets/screenshot/image_vault.png"
    file_image = "assets/screenshot/image_files.png"
    file_image2 = "assets/screenshot/image_files_chunk.png"

    # Present images in a 2x2 grid
    st.image(user_image, caption="User Collection", output_format='PNG')
    col1, col2 = st.columns(2)
    with col1:
        st.image(note_image, caption="Notes Collection", output_format='PNG')
        st.image(vault_image, caption="Vault Collection", output_format='PNG')

    with col2:
        st.image(file_image, caption="GridFS (fs.files)", output_format='PNG')
        st.image(file_image2, caption="GridFS (fs.chunks)", output_format='PNG')

    st.markdown("---")
    # ------------------------  
    # PLACEHOLDER: Architecture Diagram
    # ------------------------
    st.subheader("🔐 Encryption Flow Diagram")

    st.markdown("A simple diagram to show how AES-GCM + RSA protect your data:")

    image_path = "assets/screenshot/architecture.png"
    st.image(image_path, caption="Architecture / Encryption Flow Diagram", output_format='PNG')
    st.markdown("---")

    
elif st.session_state.page == "Notes":
    from services.views.notes import notes_page
    notes_page()

elif st.session_state.page == "Vault":
    from services.views.vault import vault_page
    vault_page()

elif st.session_state.page == "Files":
    from services.views.files import files_page
    files_page()

elif st.session_state.page == "Settings":
    from services.views.settings import delete_user
    delete_user()
