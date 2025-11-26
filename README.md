# 🔐 CryptoLab 

```
✅ **Current Status**

The *Files Section* is complete.

Users can:
- Upload files securely
- Store encrypted files in GridFS
- Download them with AES-GCM decryption
- Verify file integrity
- Delete files safely

Next phase -> *UI Revamp / Multi-Page Streamlit layout*.
```

This repository marks the **starting point** of my cryptography learning journey using Python.

Currently, it contains a collection of **practice scripts** that explore:
- File hashing
- AES encryption/decryption
- RSA key-based encryption
- Password hashing and verification

> 🧩 These scripts are part of my ongoing learning.  
> The project will evolve into a structured application as I progress further.

---

### 📁 Folder
- **practice/** → current working scripts and test files

---

### 🎥 Learning Source
Practiced alongside concepts from a YouTube course on practical cryptography to understand AES, RSA, and hashing fundamentals.

---
---

## 🔐 **Users Module Overview**

The **Users module** handles secure user registration, authentication, and cryptographic key management in CryptoLab.

Each user gets a unique RSA key pair (public/private) generated during registration, with strong password protection and key encryption.

---

### 🧠 **Core Features**

- **Secure Registration** — User passwords are hashed using `bcrypt` with unique salts.
- **RSA Key Pair Generation** — Each user receives a fresh 2048-bit RSA key pair.
- **Private Key Encryption** — The user’s private key (PEM) is encrypted using the global `master.key` before storage.
- **Public Key Storage** — The public key is stored in PEM format to enable encryption of user-specific data keys (DEKs).
- **User DEK Generation** — A random AES-based Data Encryption Key is created and encrypted with the user’s public key for future data encryption.
- **Password Verification** — Login passwords are verified using `bcrypt.checkpw()` for secure, salted authentication.

---

### 🗄️ **Database Schema (Users Collection)**

| Field | Type | Description |
| --- | --- | --- |
| `username` | `str` | Unique user identifier |
| `password_hash` | `str` | bcrypt-hashed password |
| `public_key_pem` | `str` | RSA public key (PEM format) |
| `private_key_pem_encrypted` | `str` | RSA private key encrypted with master key |
| `encrypted_user_dek` | `str` | User’s AES key (DEK) encrypted with public key |
| `date_created` | `str` | Timestamp of account creation |

---

#### 🧩 **Security Hierarchy**

```
[ Master Key 🔑 ]
     ↓
Encrypts
     ↓
[ Private Key (User) 🔒 ]
     ↓
Decrypts
     ↓
[ DEK (AES Key) 🗝️ ]
     ↓
Encrypts
     ↓
[ User Data / Notes 📄 ]

```

```
### In a Nutshell:

- Implemented user registration with bcrypt password hashing
- Added RSA keypair generation per user
- Encrypted private key PEMs using master.key
- Added encrypted user DEK for future AES data encryption
- Integrated (basic) Streamlit-based UI for registration and login 
- Verified encryption/decryption chain and key hierarchy
```
---
---


## 🗒️ **Notes Module Overview**

The **Notes module** handles secure note storage and retrieval in CryptoLab using AES-GCM encryption.

Each note is encrypted using a **user-specific DEK (AES key)** which is itself protected by RSA.

This ensures:

- Only the correct user can decrypt their notes
- No plaintext notes ever touch MongoDB
- Notes remain secure even if the database leaks

---

### 🔐 **Core Features**

- **AES-GCM Encryption** — Each note is encrypted using AES-256-GCM for confidentiality + integrity.
- **User-Specific DEK** — The DEK is unique per user and decrypted at login using their RSA private key.
- **RSA-Protected Metadata** — The DEK is stored encrypted under the user’s RSA public key.
- **Full CRUD Support** — Users can add, view, edit, and delete their encrypted notes.
- **Tamper Detection** — Stored SHA-256 digest ensures that modified ciphertext can be detected.
- **Secure ObjectId Linking** — Notes are linked to the user via `owner_id` (MongoDB ObjectId).

---

### 🗄️ **Database Schema (Notes Collection)**

| Field | Type | Description |
| --- | --- | --- |
| `owner_id` | ObjectId | User who owns the note |
| `encrypted_content` | str | AES-GCM encrypted text (base64) |
| `nonce` | str | 96-bit AES nonce (base64) |
| `sha256` | str | Integrity hash of plaintext |
| `created_at` | str | Timestamp |
| `updated_at` | str | Timestamp (optional) |

---

#### ⚙️ **Encryption Flow**

```
Login → Decrypt private.pem → Decrypt RSA-encrypted DEK → Get AES key
→ AES-GCM encrypt/decrypt notes → Store ciphertext + nonce + hash

```

```
### In a Nutshell:

- Added AES-256-GCM encryption/decryption for notes
- Integrated RSA-based DEK decryption on login
- Implemented create, view, update, delete note flows
- Added session state management for edit/update stability
- Linked notes to users via owner_id ObjectId
- Ensured all notes remain encrypted in MongoDB
```
---
---

## 🔐 **Password Vault Module Overview**

The **Vault module** adds a secure, AES-GCM encrypted password manager inside CryptoLab.

Every stored password is encrypted using the user’s DEK (Data Encryption Key), which itself is protected by the user’s RSA-encrypted key hierarchy.

This ensures that **no plaintext password is ever stored in MongoDB or exposed in transit**.

---

### 🧠 **Core Features**

- **AES-GCM Encryption**
    
    Every password is encrypted using AES-256-GCM with a fresh 96-bit nonce.
    
- **DEK-Based Encryption**
    
    Passwords are encrypted with the user's DEK, which is decrypted only after login via RSA.
    
- **Service-Based Organization**
    
    Each password belongs to a unique service (e.g., Gmail, GitHub).
    
    Services act as identifiers for CRUD operations in V1.
    
- **Password Strength Checker**
    
    Integrated `zxcvbn` scoring with feedback ensures strong passwords before saving.
    
- **Full CRUD Support**
    - Add encrypted passwords
    - View (decrypt in-memory only)
    - Edit and re-encrypt
    - Delete entries
        
        All operations stay encrypted at rest.
        
- **Zero Plaintext Storage**
    
    Neither MongoDB nor server-side logic ever handles or stores raw passwords.
    

---

### 🗄️ **Database Schema (Vault Collection)**

| Field | Type | Description |
| --- | --- | --- |
| `owner_id` | `ObjectId` | References the user who owns the entry |
| `service` | `str` | Name of the service (unique per user in V1) |
| `username` | `str` | Username/email for the service |
| `url` | `str` | URL of the service |
| `password_encrypted` | `str (Base64)` | AES-GCM ciphertext |
| `nonce` | `str (Base64)` | AES-GCM nonce used for encryption |
| `created_at` | `str` | Timestamp |

---

#### 🧩 **Security Flow**

```
User Login
    ↓
Master Key → decrypts → Private Key (PEM)
    ↓
Private Key → decrypts → User DEK (AES key)
    ↓
DEK → encrypt/decrypt → Vault Passwords (AES-GCM)

```

This ensures:

- Only the logged-in user can decrypt their vault
- No password is ever stored or transmitted in plaintext
- Database leaks reveal only AES-GCM ciphertext

```
### In a Nutshell:

- Added AES-256-GCM encrypted passwords
- Strength validation using zxcvbn
- Service-based organization
- View / Edit / Delete with in-memory decryption
- Clean UI & exact-match logic
- Zero plaintext stored in DB
```
---
---

## 📁 **Files Module Overview**

The **Files module** adds encrypted file storage to CryptoLab using **AES-GCM encryption** and **MongoDB GridFS**.

Files are encrypted client-side using the user’s DEK before storage, ensuring **zero plaintext exposure** anywhere in the database.

All files stored inside `fs.files` and `fs.chunks` remain encrypted and integrity-verified.

---

### 🧠 **Core Features**

- **AES-256-GCM Encryption**
    
    Each file is encrypted using a 32-byte DEK generated during user registration.
    
- **Secure File Uploads**
    
    Uploaded files are never stored in plaintext — only encrypted bytes + metadata go to GridFS.
    
- **GridFS Storage Structure**
    - `fs.files` → Stores metadata (filename, content_type, uploaded_at, owner_id, sha256)
    - `fs.chunks` → Stores encrypted byte chunks
- **Integrity Checking**
    
    SHA-256 hash of the original file ensures that decrypted output always matches the original.
    
- **User-Scoped Filestore**
    
    Files are tied to the authenticated user via `owner_id`.
    
- **Encrypted File Downloading**
    
    Files are decrypted on-demand using AES-GCM and offered for download.
    
- **Complete CRUD**
    - Upload
    - View metadata
    - Download (requires login)
    - Delete

---

### 🗄️ **GridFS Metadata Schema**

Each entry inside `fs.files` contains:

| Field | Description |
| --- | --- |
| `filename` | Saved file name (with `.enc` extension) |
| `metadata.owner_id` | User who uploaded the file |
| `metadata.original_filename` | Name before encryption |
| `metadata.content_type` | MIME type |
| `metadata.sha256` | Integrity hash of original file |
| `metadata.encrypted` | Always `True` |
| `metadata.uploaded_at` | Timestamp |

---

#### 🔒 **Encryption Flow**

```
[ Raw File Data ]
        ↓
AES-GCM Encrypt (using DEK)
        ↓
[ Encrypted Bytes ]
        ↓
Stored Into GridFS (fs.files + fs.chunks)

```

```
### In a Nutshell:

- AES-256-GCM encryption for all uploaded files
- GridFS integration (fs.files + fs.chunks)
- File metadata (owner_id, SHA256, MIME type, timestamps)
- Encrypted upload, download, integrity check, and delete actions
```

---
---
