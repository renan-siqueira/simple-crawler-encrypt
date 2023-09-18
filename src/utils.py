from typing import Optional
from cryptography.fernet import Fernet


def generate_key(should_generate: bool, path_key_file: str) -> Optional[bytes]:
    """
        Generate a new encryption key.
    """
    if should_generate:
        key = Fernet.generate_key()        
        with open(path_key_file, "wb") as key_file:
            key_file.write(key)

        return key
    else:
        return None
