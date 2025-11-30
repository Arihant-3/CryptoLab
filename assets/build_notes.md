# Error in users(password) : 
### 🧩 Why the error happens

You stored your hashed password like this:

```python
pwd_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

```

Here you **decoded** the hash into a string to save it in MongoDB (that’s fine).

But later, in your `verify_password()`:

```python
if bcrypt.checkpw(candidate_password.encode('utf-8'), stored_hash):

```

→ `stored_hash` is a **string**,

and `bcrypt.checkpw()` expects **bytes** for both arguments.

Hence the error:

> TypeError: argument 'hashed_password': 'str' object cannot be converted to 'PyBytes'
> 

---

### ✅ The clean fix

Just **encode the stored hash** back to bytes before comparing:

```python
if bcrypt.checkpw(candidate_password.encode('utf-8'), stored_hash.encode('utf-8')):

```

That’s it.

Now both arguments are bytes, and bcrypt can compare them safely.

---

### 🔁 The hierarchy (now perfectly correct)

```
[ Master Key 🔑 ]
     ↓
Encrypts
     ↓
[ Private Key (User) 🔒 ]
     ↓
Decrypts
     ↓
[ DEK (User AES Key) 🗝️ ]
     ↓
Encrypts
     ↓
[ User Data / Notes / Files 📄 ]

```

You’ve now implemented this chain in code form.

---

### 🧾 TL;DR Summary 

| Concept | Encrypted By | Stored Where | Purpose |
| --- | --- | --- | --- |
| **Master Key** | Nothing | Local file (`master.key`) | Protects all private keys |
| **Private Key (User)** | Master Key | MongoDB | Decrypts user’s DEK |
| **Public Key (User)** | — | MongoDB | Encrypts user’s DEK |
| **DEK (AES Key)** | User’s Public Key | MongoDB | Encrypts user data |
| **User Data** | DEK | MongoDB | Actual notes/files |


---
---
---

# Error in notes:

### **1️⃣ Public key, private key, DEK confusion**

**Problem:**

Didn’t understand how RSA keys, DEK, and master.key fit together.

**Solution:**

Clear hierarchy:

```
master.key → encrypts private.pem
private.pem → decrypts encrypted_user_dek
DEK → encrypts notes (AES-GCM)

```

This fixed the entire user → notes encryption flow.

---

### **2️⃣ Wrong use of encrypted_user_dek**

**Problem:**

Tried to use RSA-encrypted DEK directly as AES key.

**Solution:**

Correct flow:

```
encrypted_user_dek (hex) → RSA private key → base64 DEK → raw AES bytes

```

Now AES-GCM works correctly.

---

### **3️⃣ Streamlit losing state during edit/update**

**Problem:**

Clicking “Edit” showed textarea but clicking “Save” reran the script → edit mode reset → update didn’t work.

**Solution:**

Use Streamlit session state:

```python
if "editing_note" not in st.session_state:
    st.session_state["editing_note"] = None

```

Plus persist editing state with:

```python
st.session_state["editing_note"] = note_id

```

---

### **4️⃣ KeyError for editing_note**

**Problem:**

Accessing `st.session_state["editing_note"]` before initialization.

**Solution:**

Initialize before Notes section:

```python
if "editing_note" not in st.session_state:
    st.session_state["editing_note"] = None

```

---

### **5️⃣ Delete User block breaking (KeyError: username)**

**Problem:**

Delete section ran even if user wasn’t logged in → `KeyError: username`.

**Solution:**

Protect block with:

```python
if "username" not in st.session_state:
    st.error("Login to delete your account.")
    st.stop()

```

---

### **6️⃣ Edit & Delete buttons interfering in expanders**

**Problem:**

Buttons inside expanders needed unique keys to prevent collisions.

**Solution:**

Use dynamic keys:

```python
key=f"edit-{note_id}"
key=f"view-{note_id}"
key=f"del-{note_id}"

```

---

### **7️⃣ MongoDB ObjectId mismatch**

**Problem:**

Passing string `_id` instead of ObjectId.

**Solution:**

Convert consistently:

```python
ObjectId(note_id)

```

---

### **8️⃣ Page not refreshing after login**

**Problem:**

Notes section didn’t appear because login UI still displayed.

**Solution:**

Force page reload:

```python
st.rerun()

```
### ✔ `st.stop()` prevents any code from running after it

So password verification never executes if the user is not logged in.

### ✔ Prevents:

- KeyError
- Wrong user deletion
- Unlogged deletion attempts

### ✔ Secure & clean behavior

Only logged-in users can delete their accounts.


---
---
---

# Error in vault:

### **1️⃣ Duplicate Services Showing Multiple Results**

**Problem:**

Selecting a service like `"pop"` in the dropdown showed passwords for `"pop"`, `"pop2"`, `"pop3"` because the search used:

```python
"service": {"$regex": service, "$options": "i"}

```

Regex matched everything starting with or containing “pop”.

**Fix:**

Replaced regex with **exact match**:

```python
"service": service

```

Now only the chosen service appears.

---

### **2️⃣ Dropdown Displayed Services Incorrectly**

**Problem:**

`distinct("service")` returned unique service names, but since services like `pop`, `pop2`, `pop3` existed, the UI became confusing (regex grouping them together).

**Fix:**

Switching to exact-match fetch made the dropdown stable and predictable.

---

### **3️⃣ Password Strength Checker Not Integrated Initially**

**Problem:**

Vault had encryption but no visual password-strength feedback.

User could add weak passwords unknowingly.

**Fix:**

Integrated `zxcvbn` output into UI:

- Shows score (0–4)
- Shows feedback
- Blocks saving weak passwords

Gives a polished, professional feel.

---

### **4️⃣ Editing State Not Reset Properly**

**Problem:**

`editing_password` was not initialized in session state, leading to:

```
KeyError: 'editing_password'

```

**Fix:**

Added initialization:

```python
if "editing_password" not in st.session_state:
    st.session_state["editing_password"] = None

```

Also ensured that cancel/save clears the state and forces a clean `rerun()`.

---

### **5️⃣ Service Validation Logic Was Checking the Wrong Variable**

**Problem:**

Your validation accidentally used:

```python
"service": service

```

instead of:

```python
"service": new_service

```

This meant the app sometimes failed to detect duplicates or warned incorrectly.

**Fix:**

Corrected validation to properly check `new_service`.


# Error in files

### **1. Duplicate Upload Issue**

**Problem:**

Every time you clicked *Download* or *Delete*, Streamlit re-ran the entire script and re-uploaded the same file again.

This created multiple files inside `fs.files` and caused encrypted bytes to mismatch.

**Cause:**

`st.file_uploader` persists the file in session.

When Streamlit reloaded, your upload block executed again.

**Solution:**

Use a session flag like:

```python
if uploaded_file is not None and "uploaded_file_processed" not in st.session_state:
    st.session_state["uploaded_file_processed"] = True

```

and reset it only when clicking “Upload file”.

---

### **2. AES-GCM Decrypt Error: “Invalid encrypted data size”**

**Problem:**

Decryption failed because AES-GCM ciphertext length is *not* guaranteed to be a multiple of 16 bytes.

**Cause:**

Incorrect validation check:

```python
if len(encrypted_data) % 16 != 0:
    raise Exception("Invalid encrypted data size")

```

AES-GCM uses a 16-byte authentication tag, not block-based padding.

**Solution:**

Remove this check entirely.

---

### **3. Wrong slicing of nonce & ciphertext (base64 confusion earlier)**

**Problem (old version):**

The code attempted to decode parts of the encrypted file as base64 even though raw bytes were stored.

**Solution:**

Use raw bytes only:

```python
nonce = encrypted_bytes[:12]
encrypted_data = encrypted_bytes[12:]

```

This fixed decryption.

---

### **4. GridFS metadata handling mistakes**

**Problem:**

Metadata wasn’t being fetched correctly.

And some metadata fields were not being stored inside `fs.files`.

**Solution:**

Proper upload:

```python
file_id = fs.put(encrypted_bytes, filename=..., metadata={...})

```

Proper listing:

```python
db.fs.files.find({"metadata.owner_id": ObjectId(owner_id)})

```

---

### **5. Hash stored wrong (base64 earlier)**

**Problem:**

Initially SHA-256 was stored as base64-encoded text.

Not wrong, but inconsistent.

**Solution:**

Store plain hex digest:

```python
sha_digest = hashlib.sha256(data).hexdigest()

```

Easier for integrity checking.

---

### **6. Streamlit layout causing re-runs on button clicks**

**Problem:**

The *Download* → *Decrypt* → *Download Button* block created unintended UI reruns.

**Solution:**

Wrap download logic in a try/except and use session flags if needed.

After fixing duplication + decrypt logic, it works clean.

---

### **7. File uploader UI issue**

**Problem:**

Pressing “Download” immediately after upload uses the “fresh upload bytes” instead of DB bytes, since Streamlit holds them in memory.

**Solution:**

Split upload and view:

- Upload happens once
- `st.rerun()` after upload
- Listing section shows only DB files
- Download reads from GridFS only


# Error in implementing Multi-Page UI

### **1. Streamlit Auto-Rerun Breaking Navigation**

**Problem:**

Streamlit reruns the entire script on *every interaction*.

This caused:

- Forms disappearing instantly
- Page jumping back to Home
- Login/Create User UI resetting
- Buttons triggering multiple reruns

**Fix:**

Introduced a **manual router** using `st.session_state.page` and controlled reruns with:

```python
st.session_state.page = "Login"
st.rerun()

```

This stabilized navigation and created a website-like multi-page behavior.

---

### **2. Sidebar Pages Showing Default “pages/” Items**

**Problem:**

Streamlit automatically displays every script inside `/pages` in the sidebar.

This caused **unwanted entries** like:

- main
- user
- vault
- notes
- files

**Fix:**

Moved all UI pages under:

```
services/views/

```

so Streamlit wouldn’t auto-detect them as pages.

---

### **3. Create User / Login Redirect Loops**

**Problem:**

When clicking:

- **Create User**
- **Login**

Streamlit reran and bounced back to Home because sidebar selection overwrote navigation.

**Fix:**

Navigation became two-layered:

- Sidebar → only main sections
- Buttons → internal routing
    
    Using:
    

```python
if st.session_state.page != choice:
    st.session_state.page = choice
    st.rerun()

```

---

### **4. Buttons Triggering Dual Actions**

**Problem:**

Clicking one button inside Home triggered multiple reruns →

“Login” → Login page → rerun → Home again.

**Fix:**

Protected state transitions by checking previous page:

```python
if st.session_state.page == "Home":
    show_home()
elif st.session_state.page == "Login":
    login_page()

```

This ensured predictable behavior.

---

### **5. UI Forms Being Reset Automatically**

**Problem:**

Streamlit forms lose input on rerun (expected behavior).

**Fix:**

Wrapped *create user* and *login* forms inside stable middle-pages:

`"New User"` and `"Login"`

so reruns no longer wiped inputs.

---

### **6. Layout Inconsistency (Sidebar width, buttons not centered, spacing)**

**Problem:**

Streamlit default layout was uneven and cluttered.

**Fix:**

- Centralized login page using columns
- Added custom HTML headings
- Created a clean Home page with diagrams
- Put DB screenshot grid + architecture diagram