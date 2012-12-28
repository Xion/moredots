"""
Tests for the :class:`Inventory` class and related code.
"""
import os
import random
from StringIO import StringIO

import pytest

from moredots.inventory import Inventory, InventoryEntry, INVENTORY_FILE

from tests.conftest import dotfile_name
from tests.utils import random_string


# Tests

class TestInventory(object):

    def test_load_empty(self, repo_with_empty_inventory):
        inventory = Inventory(repo_with_empty_inventory)
        assert len(inventory) == 0

    def test_load_filled(self, repo_with_filled_inventory, inventory_file_path):
        inventory = Inventory(repo_with_filled_inventory)
        with open(inventory_file_path) as f:
            assert len(inventory) == len(f.readlines()) > 0


class TestInventoryEntry(object):

    def test_create_without_args(self):
        with pytest.raises(TypeError):
            InventoryEntry()

    def test_create_with_only_positional_path(self, dotfile_name):
        # need at least one other argument
        # or first one will be interpreted as textual repr. of entry
        entry = InventoryEntry(dotfile_name, hardlink=False)
        assert entry.path == dotfile_name

    def test_create_with_only_keyword_path(self, dotfile_name):
        entry = InventoryEntry(path=dotfile_name)
        assert entry.path == dotfile_name

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
def inventory_file_path(empty_repo):
    """Path to inventory file within an empty repo."""
    return os.path.join(empty_repo.dir, INVENTORY_FILE)


@pytest.fixture
def repo_with_empty_inventory(empty_repo, inventory_file_path):
    """Dotfile repo with empty inventory file (i.e. file of zero length)."""
    open(inventory_file_path, 'w').close()
    return empty_repo


@pytest.fixture
def repo_with_filled_inventory(empty_repo, inventory_file_path):
    """Dotfile repo with andomly generated inventory file
    containing at least one dotfile entry.
    """
    with open(inventory_file_path, 'w') as f:
        for _ in xrange(random.randint(1, 10)):
            InventoryEntry(dotfile_name(), hardlink=False).dump(f)
    return empty_repo


@pytest.fixture
def entry_data(dotfile_name):
    """Dictionary of keyword args for ;class:`InventoryEntry` constructor."""
    return dict(path=dotfile_name, hardlink=False)


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
