import hashlib
import base64

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def encode_b64(data: str) -> str:
    return base64.b64encode(data.encode()).decode()
