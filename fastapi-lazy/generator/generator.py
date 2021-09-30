from datetime import datetime
from math import ceil
from random import getrandbits

"""
    generate a uuid with the following format
"""


def gen_uuid() -> str:
    bytes = (
        hex(ceil(datetime.utcnow().timestamp() * 1000))[2:] + hex(getrandbits(96))[2:]
    )[:32]
    return f"{bytes[:8]}-{bytes[8:12]}-4{bytes[13:16]}-{bytes[16:19]}9-{bytes[20:32]}"
