import bcrypt


def hash_password(password: str) -> bytes:
    """Hashes a password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        bytes: The hashed password.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password: str, hashed_password: bytes) -> bool:
    """Verifies a password using bcrypt.

    Args:
        password (str): The password to verify.
        hashed_password (bytes): The hashed password.

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    return bcrypt.checkpw(password.encode(), hashed_password)
