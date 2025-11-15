import os, base64

key = base64.urlsafe_b64encode(os.urandom(32)).decode()
with open("master.key", "w") as f:
    f.write(key)
print("Master key saved to master.key")


