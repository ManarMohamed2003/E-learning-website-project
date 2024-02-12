import bcrypt
import re 

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(),salt)
    return hashed_password.decode()


def is_password_match(entered_password , stored_hash):
    stored_hash_bytes = stored_hash.encode()
    return bcrypt.checkpw(entered_password.encode(),stored_hash_bytes)


def is_strong_password(password):
    min_length = 8

    if len(password) < min_length:
        return False
    elif not any( char.isupper() for char in password):
        return False
    elif not any( char.islower() for char in password):
        return False     
    elif not any( char.isdigit() for char in password):
        return False
    elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]" , password):
        return False

    return True   