"""
Module containing the :class:`Inventory` class which contains
meta-information about dotfiles stored within dotfile repository.
"""
import os
from itertools import imap


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

        self._entries = {}
        if os.path.exists(self.file):
            self.load()

    def load(self):
        """Loads inventory records from ``self.file``."""
        with open(self.file) as f:
            self._entries = dict(
                (entry.path, entry)
                for entry in imap(InventoryEntry, f.readlines())
            )
            self._dirty = False

    def save(self):
        """Saves inventory records to ``self.file``."""
        with open(self.file, 'w') as f:
            for entry in self:
                entry.dump(f)

            self.repo.git_repo.index.add([INVENTORY_FILE])
            self._dirty = False

    def add(self, path, **kwargs):
        """Adds a dotfile to this inventory.

        :param path: Path to the dotfile, relative to repository root directory

        Additional keyword arguments are stored within the inventory entry
        for the file.
        """
        if not path:
            raise ValueError("no dotfile path specified")
        if path in self:
            raise ValueError(
                "dotfile %s already exists in the inventory" % path)

        self._entries[path] = InventoryEntry(path, **kwargs)
        self._dirty = True

    def update(self, path, **kwargs):
        """Updates entry data for given dotfile.

        :param path: Path to the dotfile, relative to repository root directory

        Keyword arguments specify which entry data should be updated
        and new values for the keys.
        """
        if not path:
            raise ValueError("no dotfile path specified")
        if path not in self:
            raise ValueError(
                "dotfile %s does not exist in the inventory" % path)
        if not kwargs:
            raise TypeError("update() requires at least one keyword argument")

        entry = self._entries[path]
        for name, value in kwargs.iteritems():
            setattr(entry, name, value)
            self._dirty = True

    def remove(self, path):
        """Removes dotfile from this inventory.
        :param path: Path to the dotfile, relative to repository root directory
        """
        if not path:
            raise ValueError("no dotfile path specified")
        if path not in self:
            raise ValueError(
                "dotfile %s does not exist in the inventory" % path)

        del self._entries[path]
        self._dirty = True

    @property
    def file(self):
        """Full path to the inventory data file."""
        return os.path.join(self.repo.dir, INVENTORY_FILE)

    @property
    def dirty(self):
        """Flag indicating whether inventory was saved since last change."""
        return self._dirty

    def __nonzero__(self):
        """Casting to bool yields True if inventory contains entries."""
        return bool(self._entries)
    __bool__ = __nonzero__  # for Python 3.x

    def __contains__(self, path):
        """Operator `in` allows to check if dotfiles exists in inventory."""
        return path in self._entries

    def __len__(self):
        """Length of :class:`Inventory` equals number of its entries."""
        return len(self._entries)

    def __iter__(self):
        """Iterating through :class:`Inventory` object will yield
        all the :class:`InventoryEntry` objects contained within.
        """
        return self._entries.itervalues()

    def __getitem__(self, path):
        """Indexing retrieves :class:`InventoryEntry` object
        corresponding to dotfile of given path.
        """
        return self._entries[path]

    def __enter__(self):
        """Using :class:`Inventory` as context manager ensures :meth:`save`
        is called at the end of ``with`` block.
        """
        return self  # __exit__ does all the work

    def __exit__(self, type, value, traceback):
        """Exiting ``with`` block always calls :meth:`save`."""
        self.save()


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
