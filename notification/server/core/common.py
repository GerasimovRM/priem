from ..config import DEBUG


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)