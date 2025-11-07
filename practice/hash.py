import hashlib

# text = "Hello, World!"
# print("Original text:", text)
# print(text.encode())
# hash_object = hashlib.sha256(text.encode())
# print(hash_object)
# hash_digest = hash_object.hexdigest()
# print("SHA-256 Hash:", hash_digest)

def hash_file(file_path):
    """This function returns the SHA-256 hash
    of the file passed into it"""

    h = hashlib.new('sha256')
    
    with open(file_path, 'rb') as file:
        # Read and update hash string value in blocks of 4K
        while True:
            chunk = file.read(1024)
            if chunk == b"":
                break
            h.update(chunk)
        
    return h.hexdigest()

def verify_integrity(file1, file2):
    """This function compares the SHA-256 hash
    of two files"""

    hash1 = hash_file(file1)
    hash2 = hash_file(file2)
    print("Checking the integrity between the two files...")
    if hash1 == hash2:
        return "File is intact, no modifications have been made."
    return "File has been modified, hashes do not match!"


if __name__ == "__main__":
    file_path = "Sample.txt"
    print(f"The SHA-256 hash of the file {file_path} is:")
    print(hash_file(file_path))
    print(verify_integrity("image1.png", "image2.png"))
    print(verify_integrity("image1.png", "image3.png"))
    