"""
Tests for subsequent adding files to
and then removing them from :class:`DotfileRepo`.
"""
from tests.test_repo import dotfile_exists, dotdir_file_exists


def test_add_and_remove_file(empty_repo, dotfile_in_home):
    repo = empty_repo
    repo.add(dotfile_in_home)
    repo.remove(dotfile_in_home)

    assert not dotfile_exists(dotfile_in_home, repo)


def test_add_and_remove_dotdir_file(empty_repo, home_dir, dotdir_file_in_home):
    repo = empty_repo
    repo.add(dotdir_file_in_home)
    repo.remove(dotdir_file_in_home)

    assert not dotdir_file_exists(dotdir_file_in_home, home_dir, repo)
