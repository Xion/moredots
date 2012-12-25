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
        :param: :class:`DotfileRepo` object
        """
        self.repo = repo

    @property
    def file(self):
        """Full path to the inventory data file."""
        return os.path.join(self.repo.dir, INVENTORY_FILE)


class InventoryEntry(object):
    """Represents a single entry in the inventory that contains information
    about a dotfile stored within dotfile repository.
    """
    __slots__ = ['path', 'hardlink']

    def __init__(self, *args, **kwargs):
        """Constructor.

        Entry is initializaed based on both positional and keyword arguments.
        Dotfile repo (relative to repo root) is expected as first argument.
        """
        for name, value in zip(self.__slots__, args):
            if name in kwargs:
                raise TypeError("__init__() got multiple values "
                                "for keyword argument '%s'" % name)
            kwargs[name] = value

        # initialize the record
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

    def dumps(self, sep=':', include_path=True):
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
