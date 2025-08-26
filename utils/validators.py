import re

def validate_email(email: str) -> bool:
    """Validates email format."""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_phone(phone: str) -> bool:
    """Validates phone number format (basic)."""
    return bool(re.match(r"^\+?\d{7,15}$", phone))
