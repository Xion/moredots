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

    def test_load_empty(self, empty_inventory):
        assert len(empty_inventory) == 0

    def test_load_filled(self, filled_inventory, inventory_file_path):
        with open(inventory_file_path) as f:
            assert len(filled_inventory) == len(f.readlines()) > 0

    def test_add_requires_path(self, empty_inventory):
        with pytest.raises(ValueError):
            empty_inventory.add("")

    def test_add_fails_on_existing(self, filled_inventory, dotfile_in_inventory):
        with pytest.raises(ValueError):
            filled_inventory.add(dotfile_in_inventory)

    def test_add_creates_entry(self, empty_inventory, dotfile_name):
        inv = empty_inventory
        inv.add(dotfile_name)

        assert len(inv) == 1
        assert dotfile_name in inv

    def test_add_saves_kwargs(self, empty_inventory, dotfile_name):
        repo = empty_inventory
        repo.add(dotfile_name, hardlink=True)

        assert repo[dotfile_name].hardlink == True

    def test_update_requires_existing(self, empty_inventory, dotfile_name):
        with pytest.raises(ValueError):
            empty_inventory.update(dotfile_name, hardlink=True)

    def test_update_requires_kwargs(self, filled_inventory, dotfile_in_inventory):
        with pytest.raises(TypeError):
            filled_inventory.update(dotfile_in_inventory)

    def test_update_works(self, filled_inventory, dotfile_in_inventory):
        filled_inventory.update(dotfile_in_inventory, hardlink=True)
        assert filled_inventory[dotfile_in_inventory].hardlink == True

    def test_remove_requires_path(self, empty_inventory):
        with pytest.raises(ValueError):
            empty_inventory.remove("")

    def test_remove_requires_existing(self, empty_inventory, dotfile_name):
        with pytest.raises(ValueError):
            empty_inventory.remove(dotfile_name)

    def test_remove_works(self, filled_inventory, dotfile_in_inventory):
        count_before = len(filled_inventory)
        filled_inventory.remove(dotfile_in_inventory)
        count_after = len(filled_inventory)

        assert count_before == count_after + 1


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
def empty_inventory(empty_repo, inventory_file_path):
    """Inventory object based on zero-size inventor file."""
    open(inventory_file_path, 'w').close()
    return Inventory(empty_repo)


@pytest.fixture
def filled_inventory(empty_repo, inventory_file_path):
    """Inventory object based on randomly generated inventory file
    containing at least one dotfile entry.
    """
    with open(inventory_file_path, 'w') as f:
        for _ in xrange(random.randint(1, 10)):
            InventoryEntry(dotfile_name(), hardlink=False).dump(f)
    return Inventory(empty_repo)


@pytest.fixture
def dotfile_in_inventory(filled_inventory):
    """Path to dotfile which is already in a inventory."""
    return next(iter(filled_inventory)).path


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
