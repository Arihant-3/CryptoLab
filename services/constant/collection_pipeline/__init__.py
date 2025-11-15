# Collection Pipeline constant

'''
- `users`
    - `_id`, `username`, `password_hash` (bcrypt), `public_key_pem`, `private_key_pem_encrypted`, `encrypted_user_dek`, `date_created`
'''

DATABASE_NAME: str = "CryptoLabDB"
COLLECTION_USERS: str = "Users"

