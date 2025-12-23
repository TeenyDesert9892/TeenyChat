import random
import socket

from string import digits, ascii_letters, punctuation

def secret_key_generator(length: int) -> str:
    return "".join([random.choice(digits+ascii_letters+punctuation) for i in range(length)])

def get_host_ip() -> str:
    return socket.gethostbyname(socket.gethostname())