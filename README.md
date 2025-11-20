# 🔐 CryptoLab 

```
✅ **Current Status**

The *Notes section* supports:

- Creating encrypted notes
- Viewing decrypted notes
- Editing with persisted session state
- Deleting notes
- Securely managing everything with user-specific AES keys

Notes are fully functional and integrated with the user authentication layer.

Next phase -> *Vault Module*: Implementing storage for User secrets as per services.
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

### 🔐 **Users Module Overview**

The **Users module** handles secure user registration, authentication, and cryptographic key management in CryptoLab.

Each user gets a unique RSA key pair (public/private) generated during registration, with strong password protection and key encryption.

---

#### 🧠 **Core Features**

- **Secure Registration** — User passwords are hashed using `bcrypt` with unique salts.
- **RSA Key Pair Generation** — Each user receives a fresh 2048-bit RSA key pair.
- **Private Key Encryption** — The user’s private key (PEM) is encrypted using the global `master.key` before storage.
- **Public Key Storage** — The public key is stored in PEM format to enable encryption of user-specific data keys (DEKs).
- **User DEK Generation** — A random AES-based Data Encryption Key is created and encrypted with the user’s public key for future data encryption.
- **Password Verification** — Login passwords are verified using `bcrypt.checkpw()` for secure, salted authentication.

---

#### 🗄️ **Database Schema (Users Collection)**

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


### 🗒️ **Notes Module Overview**

The **Notes module** handles secure note storage and retrieval in CryptoLab using AES-GCM encryption.

Each note is encrypted using a **user-specific DEK (AES key)** which is itself protected by RSA.

This ensures:

- Only the correct user can decrypt their notes
- No plaintext notes ever touch MongoDB
- Notes remain secure even if the database leaks

---

#### 🔐 **Core Features**

- **AES-GCM Encryption** — Each note is encrypted using AES-256-GCM for confidentiality + integrity.
- **User-Specific DEK** — The DEK is unique per user and decrypted at login using their RSA private key.
- **RSA-Protected Metadata** — The DEK is stored encrypted under the user’s RSA public key.
- **Full CRUD Support** — Users can add, view, edit, and delete their encrypted notes.
- **Tamper Detection** — Stored SHA-256 digest ensures that modified ciphertext can be detected.
- **Secure ObjectId Linking** — Notes are linked to the user via `owner_id` (MongoDB ObjectId).

---

#### 🗄️ **Database Schema (Notes Collection)**

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



