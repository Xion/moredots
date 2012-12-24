"""
Module containing code for manipulating file paths,
auxiliary to various other places in the project.
"""
import os


# Directory assertions

def ensure_empty_dir(path):
    """Checks if given directory is empty, throwing ``IOError`` if not."""
    if os.path.isdir(path) and len(os.listdir(path)) > 0:
        raise IOError("%s is not empty" % path)


def ensure_existing_dir(path):
    """Checks if given directory exists, throwing ``IOError`` if it doesn't."""
    if not os.path.exists(path):
        raise IOError("%s does not exist" % path)
    if not os.path.isdir(path):
        raise IOError("%s is not a directory" % path)


# Other

def remove_dot(path):
    """Removes the leading dot from the childmost path fragment.
    :return: Modified path
    """
    rest = ""

    while True:
        path, curr = os.path.split(path)
        if not (path or curr):
            return path

        if len(curr) > 1 and curr.startswith('.') and curr != '..':
            result = os.path.join(path, curr[1:], rest)
            return result.rstrip(os.path.sep)

        rest = os.path.join(curr, rest)


def restore_dot(path):
    """Adds the leading to the beginning of a relative path,
    if it isn't present there already.
    :return: Modified path
    """
    if os.path.isabs(path):
        raise ValueError("relative path expected")

    # put dot at beginning of first actual path segment that lacks it
    parts = path.split(os.path.sep)
    for i, part in enumerate(parts):
        if part in ('.', '..'):
            continue
        if not part.startswith('.'):
            parts[i] = "." + part
            break

    return os.path.sep.join(parts)
