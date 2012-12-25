"""
Tests for the :class:`Inventory` class and related code.
"""
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
        #  or first one will be interpreted as textual repr. of entry
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


# Fixtures / resources

@pytest.fixture
def dotfile_path():
    """Random dotfile path."""
    return random_string(length=32)


@pytest.fixture
def entry_data(dotfile_path):
    """Dictionary of keyword args for ;class:`InventoryEntry` constructor."""
    return dict(path=dotfile_path, hardlink=False)
