import json
import time
import random
import string
from urllib.parse import urlparse

def now_ms():
    return int(time.time() * 1000)

def domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""

def safe_json_dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)

def generate_fake_credentials():
    """Simple static fallback credentials for config"""
    return {
        "email": f"test{random.randint(1000, 9999)}@gmail.com",
        "username": f"testuser{random.randint(1000, 9999)}",
        "password": f"TestPass{random.randint(1000, 9999)}!",
        "phone": f"+1202555{random.randint(1000, 9999)}",
        "firstname": "Test",
        "lastname": "User",
        "address": "123 Test Street",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90001"
    }