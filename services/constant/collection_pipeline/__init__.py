# Collection Pipeline constant

'''
- `users`
    - `_id`, `username`, `password_hash` (bcrypt), `public_key_pem`, `private_key_pem_encrypted`, `encrypted_user_dek`, `date_created`
- `notes`
    - `_id`, `owner_id`, `encrypted_content`, `iv` or 'nonce', `sha256`, `created_at`, `updated_at
- `vault` (passwords)
    - `_id`, `owner_id`, `service`, `username`, `password_encrypted`, `iv`, `url`, `created_at`
'''

DATABASE_NAME: str = "CryptoLabDB"
COLLECTION_USERS: str = "Users"
COLLECTION_NOTES: str = "Notes"
COLLECTION_VAULT: str = "Vault"
