"""
Tests for the :class:`Inventory` class and related code.
"""
import os
import string
from StringIO import StringIO

import pytest

from moredots.inventory import Inventory, InventoryEntry

from tests.utils import random_string


# Tests

class TestInventoryEntry(object):

    def test_create_without_args(self):
        with pytest.raises(TypeError):
            InventoryEntry()

    def test_create_with_only_positional_path(self, dotfile_path):
        # need at least one other argument
        # or first one will be interpreted as textual repr. of entry
        entry = InventoryEntry(dotfile_path, hardlink=False)
        assert entry.path == dotfile_path

    def test_create_with_only_keyword_path(self, dotfile_path):
        entry = InventoryEntry(path=dotfile_path)
        assert entry.path == dotfile_path

    def test_create_with_keyword_args(self, entry_data):
        entry = InventoryEntry(**entry_data)

        for name, expected in entry_data.iteritems():
            actual = getattr(entry, name)
            assert expected == actual

    def test_dumps(self, entry, entry_dump):
        assert entry.dumps() == entry_dump

    def test_dump(self, entry, entry_dump):
        f = StringIO()
        entry.dump(f)

        f.seek(0)
        assert f.read() == entry_dump + os.linesep

    def test_loads(self, entry, entry_dump):
        # change path before loading from dump
        path = entry.path
        entry.path = random_string()

        # verify it's correctly overwritten back
        entry.loads(entry_dump)
        assert entry.path == path

    def test_load(self, entry, entry_dump):
        # flow like im test_loads
        path = entry.path
        entry.path = random_string()

        entry.load(StringIO(entry_dump))
        assert entry.path == path

    def test_str(self, entry, entry_dump):
        assert str(entry) == entry_dump


# Fixtures / resources

@pytest.fixture
def dotfile_path():
    """Random dotfile path."""
    return random_string(chars=string.ascii_lowercase + '/', length=32)


@pytest.fixture
def entry_data(dotfile_path):
    """Dictionary of keyword args for ;class:`InventoryEntry` constructor."""
    return dict(path=dotfile_path, hardlink=False)


@pytest.fixture
def entry(entry_data):
    """Pre-constructed :class:`InventoryEntry` object."""
    return InventoryEntry(**entry_data)


@pytest.fixture
def entry_dump(entry_data):
    """Dumped text representation of :class:`InventoryEntry` data."""
    path = entry_data['path']
    rest = os.pathsep.join("%s=%s" % (name, value)
                           for name, value in entry_data.iteritems()
                           if name != 'path')
    return path + os.pathsep + rest
