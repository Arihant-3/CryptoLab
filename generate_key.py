import os, base64

key = base64.urlsafe_b64encode(os.urandom(32)).decode()
with open(".streamlit\secrets.toml", "a") as f:
    f.write(f'''\nMASTER_KEY = "{key}"''')
print("Master key saved to .streamlit\secrets.toml")


