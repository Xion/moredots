"""
Various utility code.
"""


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
    for name in ['get', 'set', 'del']:
        if name in property_funcs:
            property_funcs['f' + name] = property_funcs.pop(name)

    docstring = func.func_doc
    return property(doc=docstring, **property_funcs)
