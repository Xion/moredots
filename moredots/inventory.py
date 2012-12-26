"""
Module containing the :class:`Inventory` class which contains
meta-information about dotfiles stored within dotfile repository.
"""
import os


__all__ = ['Inventory']


INVENTORY_FILE = '.mdots_files'


class Inventory(object):
    """Represents the inventory list of dotfiles contained within repository.

    Inventory is simple, text-based database which stores additional information
    specific to particular dotfile, necessary for conducting moredots operations
    correctly with respect to that dotfile.

    As an example, inventory will store whether the dotfile should be
    symlinked or hardlinked from $HOME to repo directory.
    """
    def __init__(self, repo):
        """Constructor.
        :param repo: :class:`DotfileRepo` object
        """
        self.repo = repo
        self.load()

    def load(self):
        """Loads inventory records from ``self.file``."""
        entries = {}
        with open(self.file) as f:
            for entry in map(InventoryEntry, f.readlines()):
                entries[entry.path] = entry
        self._entries = entries

    def save(self):
        """Saves inventory records to ``self.file``."""
        with open(self.file, 'w') as f:
            for entry in self.entries.itervalues():
                entry.dumps(f)

    @property
    def file(self):
        """Full path to the inventory data file."""
        return os.path.join(self.repo.dir, INVENTORY_FILE)

    def __nonzero__(self):
        """Casting to bool yields True if inventory contains entries."""
        return bool(self._entries)
    __bool__ = __nonzero__  # for Python 3.x

    def __len__(self):
        """Length of :class:`Inventory` equals number of entries."""
        return len(self._entries)

    def __iter__(self):
        """Iterating through :class:`Inventory` object will yield
        all the :class:`InventoryEntry` objects contained within.
        """
        return self._entries.itervalues()

    def __getitem__(self, path):
        """Indexing retrieves :class:`InventoryEntry` object corresponding to
        dotfile of given path.
        """
        return self._entries[path]


class InventoryEntry(object):
    """Represents a single entry in the inventory that contains information
    about a dotfile stored within dotfile repository.
    """
    __slots__ = ['path', 'hardlink']

    def __init__(self, *args, **kwargs):
        """Constructor.

        Entry is initialized either from keyword arguments only,
        or dotfile path along with keyword arguments,
        or a single positional argument which contains the entry's
        textual representation.

        Examples::

            entry = InventoryEntry(path='.foo', hardlink=False)
            entry = InventoryEntry('.foo', hardlink=False)
            entry = InventoryEntry('.foo:hardlink=False')

        """
        argcount = len(args) + len(kwargs)
        if argcount == 0 or argcount > len(self.__slots__):
            raise TypeError("__init__() takes exactly %s arguments (%s given)"
                            % (len(self.__slots__), argcount))

        # parse textual representation if provided
        if len(args) == 1 and not kwargs:
            self.loads(args[0])
            return

        # put positional args into kwargs dictionary
        for name, value in zip(self.__slots__, args):
            if name in kwargs:
                raise TypeError("__init__() got multiple values "
                                "for keyword argument '%s'" % name)
            kwargs[name] = value

        # initialize the record based on kwargs
        for name, value in kwargs.iteritems():
            if name not in self.__slots__:
                raise TypeError("__init__() got an unexpected keyword argument "
                                "'%s'" % name)
            setattr(self, name, value)

    def __str__(self):
        """Textual representation of inventory entry,
        fit for writing it directly into inventory file.
        """
        return self.dumps()

    def __repr__(self):
        """Internal text representation of the entry for debugging purposes."""
        return "<%s %s %s>" % (self.__class__.__name__, self.path,
                               self.dumps(sep=" ", include_path=False))

    def dump(self, f, sep=os.pathsep, include_path=True):
        """Dump the entry into its textual representation,
        writing it to specified file-like object.

        For description of other parameters, see :meth:`dumps`.
        """
        print >>f, self.dumps(sep=sep, include_path=include_path)

    def dumps(self, sep=os.pathsep, include_path=True):
        """Dump the entry into its textual representation.

        :param sep: Separator inserted between the values
        :param include_path: Whether path (as standalone value, without key)
                             should be included at the beginning
        """
        data = ((name, getattr(self, name)) for name in self.__slots__
                if name != 'path')

        result = sep.join("%s=%s" % kvp for kvp in data)
        if include_path:
            result = self.path + sep + result
        return result

    def load(self, f, sep=os.pathsep):
        """Load the entry data for textual representation,
        read from specified file-like object.

        For description of other parameters, see :meth:`loads`.
        """
        return self.loads(f.readline(), sep=sep)

    def loads(self, text, sep=os.pathsep):
        """Load the entry data from textual representation thereof.

        :param sep: Separator inserted between the values

        :raise: ``ValueError`` if parsing error occurs
        """
        text = str(text).strip()
        if not text:
            raise ValueError("no data provided decode inventory entry")

        parts = text.split(sep)
        if not parts:
            raise ValueError("data lacks proper structure of inventory entry")

        data = {'path': parts[0]}
        for part in parts[1:]:
            name, value = part.split('=')  # unpack errors slipping is fine here
            if name in data:
                raise ValueError("duplicate value for '%s' key" % name)
            data[name] = value

        # parsing successful, copy values to self
        for name, value in data.iteritems():
            setattr(self, name, value)
