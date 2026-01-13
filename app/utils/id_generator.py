import uuid
import string

BASE62 = string.ascii_letters + string.digits

def base62_encode(number: int) -> str:
    base = len(BASE62)

    result = []
    while number:
        number, reminder = divmod(number, base)
        result.append(BASE62[reminder])
    
    return ''.join(result) or "0"

def generate_short_code() -> str:
    return base62_encode(uuid.uuid4().int)[:8]
