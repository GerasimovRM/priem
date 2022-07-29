import os

from dotenv import load_dotenv


def debug_prestring(st: str) -> str:
    if DEBUG:
        return "DEBUG_" + st
    return st


load_dotenv()

DEBUG = True if os.getenv("DEBUG") in ("True", "true", "1") else False

MONGODB_URL = os.getenv(debug_prestring("MONGODB_URL"))
print(MONGODB_URL)
PARSE_EVERY = int(os.getenv("PARSE_EVERY"))
