import hashlib
import secrets

# Controls how expensive password hashing is; higher values make brute force attacks slower.
PASSWORD_HASH_ITERATIONS = 600_000


# Turns a plain password into a salted hash before it is stored in the database.
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()

    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt}${password_hash}"


# Checks a login password against the stored password hash without exposing the plain password.
def verify_password(password: str, stored_password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_hash = stored_password_hash.split("$")
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()

    return secrets.compare_digest(password_hash, expected_hash)


# Creates a random opaque access token that can be stored and checked later.
def generate_token() -> str:
    return secrets.token_urlsafe(32)
