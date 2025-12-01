import base64
from uuid import uuid4

def make_token_plain() -> str:
    b = uuid4().bytes
    return base64.urlsafe_b64encode(b).decode().rstrip("=")