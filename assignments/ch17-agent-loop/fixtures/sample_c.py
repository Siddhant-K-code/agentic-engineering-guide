from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None

def get_user(user_id: int) -> User:
    return User(id=user_id, name="Alice")
