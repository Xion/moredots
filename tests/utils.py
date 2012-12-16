"""
Utility code used by tests.
"""
import random
import string


def random_string(chars=string.printable, length=32):
    """Generates a random string of given length."""
    return "".join(random.choice(chars) for _ in xrange(length))
