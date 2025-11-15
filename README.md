# 🔐 CryptoLab 

```
✅ **Current Status**

The *User Section* is complete.

Users can:

- Register securely
- Have their keys safely generated and stored
- Authenticate using salted password hashes

Next phase -> *Notes Section*: implementing AES-based encryption/decryption using the user's RSA-managed DEK.
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

### 🧩 **Security Hierarchy**

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


