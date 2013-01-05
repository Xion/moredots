"""
Tests for adding files to :class:`DotfileRepo`.
"""
import os

import pytest

from moredots import exc

from tests.test_repo import dotfile_exists, dotdir_file_exists


class TestAdd(object):

    def test_add_file_to_empty(self, empty_repo, dotfile_in_home):
        repo = empty_repo
        repo.add(dotfile_in_home)
        assert dotfile_exists(dotfile_in_home, repo)

    def test_add_file_to_nonempty(self, filled_repo, dotfile_in_home):
        repo = filled_repo
        repo.add(dotfile_in_home)
        assert dotfile_exists(dotfile_in_home, repo)

    def test_add_existing_file(self, empty_repo, dotfile_in_home):
        repo = empty_repo
        repo.add(dotfile_in_home)

        with pytest.raises(exc.DuplicateDotfileError):
            repo.add(dotfile_in_home)

    def test_add_dotdir_file_to_empty(self, empty_repo, home_dir,
                                      dotdir_file_in_home):
        repo = empty_repo
        repo.add(dotdir_file_in_home)
        assert dotdir_file_exists(dotdir_file_in_home, home_dir, repo)

    def test_add_dotdir_file_to_nonempty(self, filled_repo, home_dir,
                                         dotdir_file_in_home):
        repo = filled_repo
        repo.add(dotdir_file_in_home)
        assert dotdir_file_exists(dotdir_file_in_home, home_dir, repo)

    def test_add_existing_dotdir_file(self, empty_repo, home_dir,
                                      dotdir_file_in_home):
        repo = empty_repo
        repo.add(dotdir_file_in_home)

        with pytest.raises(exc.DuplicateDotfileError):
            repo.add(dotdir_file_in_home)

    def test_add_file_as_hardlink(self, empty_repo, dotfile_in_home):
        repo = empty_repo
        repo.add(dotfile_in_home, hardlink=True)

        _, name = os.path.split(dotfile_in_home)
        dotfile_in_repo = os.path.join(repo.dir, name[1:])
        assert (os.path.exists(dotfile_in_repo)
                and not os.path.islink(dotfile_in_repo))
        assert os.path.exists(dotfile_in_home)

    def test_add_dotdir_file_as_hardlink(self, empty_repo, home_dir,
                                         dotdir_file_in_home):
        repo = empty_repo
        repo.add(dotdir_file_in_home, hardlink=True)

        dotdir_file = os.path.relpath(dotdir_file_in_home, start=home_dir)
        dotdir_file_in_repo = os.path.join(repo.dir, dotdir_file[1:])

        assert (os.path.exists(dotdir_file_in_repo)
                and not os.path.islink(dotdir_file_in_repo))
        assert os.path.exists(dotdir_file_in_home)
