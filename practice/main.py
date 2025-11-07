from practice.hash import hash_file, verify_integrity
from encryption import aes_ed, rsa_ed
from practice.password import check_password_strength, hash_password, verify_password
from getpass import getpass

def menu():
    print("\nSelect an option:")
    print("1. Hash a file")
    print("2. Verify file integrity")
    print("3. AES Encrypt/Decrypt")
    print("4. RSA Encrypt/Decrypt")
    print("5. Check password strength")
    print("0. Exit")
    

print('''
Initializing Cryptography Toolkit...

Welcome Agent! Your mission, should you choose to accept it, is to utilize this toolkit for secure operations.
- Analyze and hash files to detect tampering.
- Encrypt and decrypt sensitive data using AES and RSA algorithms.
- Ensure password strength and manage credentials securely.

All systems are go. Proceed with caution and precision.
Good luck, and stay secure!    
''')

while True:
    menu()
    choice = input("Enter your choice (1-5): ")
    if choice == '0':
        break
    
    elif choice == '1':
        file_path = input("Enter the file path to hash: ")
        print("File Hash:", hash_file(file_path))
    
    elif choice == '2':
        file1 = input("Enter the path of the first file: ")
        file2 = input("Enter the path of the Second file: ")
        print(verify_integrity(file1, file2))
        
    elif choice == '3':
        message = input("Enter the message to AES encrypt/decrypt: ")
        print("AES Encryption/Decryption:")
        key, ciphertext, plaintext = aes_ed(message)
        print(f"AES Key: {key}")
        print(f"Ciphertext: {ciphertext}")
        print(f"Decrypted Plaintext: {plaintext}")
        
    elif choice == '4':
        message = input("Enter the message to RSA encrypt/decrypt: ")
        print("RSA Encryption/Decryption:")
        ciphertext, plaintext = rsa_ed(message)
        print(f"RSA message, encrypted with a public key: {ciphertext}")
        print(f"RSA message, decrypted with a private key:  {plaintext}")
        
    elif choice == '5':
        while True:
            pwd = getpass("Enter password to check strength: ")
            response = check_password_strength(pwd)
            print(response)
            if response.__contains__("Weak"):
                print("Please try again with a stronger password.\n")
            else:
                break
        
        hashed_pwd = hash_password(pwd)
        print(f"Your hashed password is: {hashed_pwd.decode()}\n")
        
        attempt = getpass("Re-enter your password for verification: ")
        print(verify_password(attempt, hashed_pwd))
    
    else:
        print("Invalid choice. Please select a valid option.")

print("Agent, you are exiting the cryptography toolkit. Stay sharp and secure out there!")


