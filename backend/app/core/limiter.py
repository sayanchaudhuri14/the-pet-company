from slowapi import Limiter
from slowapi.util import get_remote_address

# Single shared limiter instance used by both main.py and route modules.
# Centralising here ensures test fixtures can reset() the correct instance.
limiter = Limiter(key_func=get_remote_address)
