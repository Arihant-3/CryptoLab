from zxcvbn import zxcvbn
from getpass import getpass
import bcrypt

def check_password_strength(password):
    """
    Check the strength of a given password using the zxcvbn library.

    Args:
        password (str): The password to be evaluated.

    Returns:
        dict: A dictionary containing the strength score and feedback.
    """
    result = zxcvbn(password)
    score = result["score"]
    if score == 3:
        response = f"Password is strong but could be improved, score: {score}."
        
    elif score > 3:
        response = f"Password is very strong, score: {score}."
        
    else:
        feedback = result["feedback"]
        warning = feedback.get("warning")
        suggestions = feedback.get("suggestions")
        response = f"Weak Password. Score is {str(score)}."
        response += f"\nWarning: {warning if warning else 'None'}"
        response += "\nSuggestions:"
        for suggestion in suggestions:
            response += " " + suggestion

    return response

def hash_password(password):
    """
    Hash a given password using bcrypt.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    # Generate a salt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed

def verify_password(password_attempt, hashed):
    """
    Verify a given password against a hashed password.

    Args:
        password (str): The plain text password to verify.
        hashed (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    if bcrypt.checkpw(password_attempt.encode(), hashed):
        return "Password is correct. Access granted."
    else:
        return "Incorrect Password. Access denied!"


if __name__ == "__main__":
    while True:
        # getpass hides the password input in the terminal
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
    
    
    