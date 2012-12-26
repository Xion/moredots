"""
Various utility code.
"""
import os


def objectproperty(func):
    """Alternate version of the standard ``@property`` decorator,
    useful for proeperties that expose setter (or deleter) in addition to getter.

    It allows to contain all two/three functions and prevent PEP8 warnings
    about redefinion of ``x`` when using ``@x.setter`` or ``@x.deleter``.

    Usage::

        @objectproperty
        def foo():
            '''The foo property.'''
            def get(self):
                return self._foo
            def set(self, value):
                self._foo = value
            return locals()

    Note that ``return locals()`` at the end is required.
    """
    property_funcs = func()

    # see if we need to rename some of the functions returned
    for name in ('get', 'set', 'del'):
        if name in property_funcs:
            property_funcs['f' + name] = property_funcs.pop(name)

    return property(doc=func.func_doc, **property_funcs)


# Path manipulation

def relative_path(path, base):
    """Turns given path into relative one (wrt to given base)
    if the path isn't relative already.
    :return: Relative ``path``
    """
    if os.path.isabs(path):
        return os.path.relpath(path, start=base)
    return path


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
