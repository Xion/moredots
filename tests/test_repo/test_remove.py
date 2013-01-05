"""
Tests for removing files from :class:`DotfileRepo`.
"""
import os

import pytest

from moredots import exc


class TestRemove(object):

    def test_remove_existing_file(self, filled_repo):
        repo = filled_repo

        dotfile = next(repo.dotfiles).path
        repo.remove(dotfile)

        assert not os.path.exists(os.path.join(repo.dir, dotfile))

    def test_remove_nonexistent_file(self, filled_repo):
        repo = filled_repo

        dotfile = next(repo.dotfiles).path + '_does_not_exist'
        with pytest.raises(exc.DotfileNotFoundError):
            repo.remove(dotfile)

    def test_remove_same_file_twice(self, filled_repo):
        repo = filled_repo
        dotfile = next(repo.dotfiles).path

        repo.remove(dotfile)
        with pytest.raises(exc.DotfileNotFoundError):
            repo.remove(dotfile)

    def test_remove_existing_dotdir_file(self, filled_repo):
        repo = filled_repo

        dotdir_file = next(df for df in repo.dotfiles
                           if os.path.sep in df.path).path
        repo.remove(dotdir_file)

        assert not os.path.exists(os.path.join(repo.dir, dotdir_file))

    def test_remove_nonexistent_dotdir_file(self, filled_repo):
        repo = filled_repo

        dotdir_file = next(df for df in repo.dotfiles
                           if os.path.sep in df.path).path + '_does_not_exist'
        with pytest.raises(exc.DotfileNotFoundError):
            repo.remove(dotdir_file)

    def test_remove_same_dotdir_file_twice(self, filled_repo):
        repo = filled_repo
        dotdir_file = next(df for df in repo.dotfiles
                           if os.path.sep in df.path).path

        repo.remove(dotdir_file)
        with pytest.raises(exc.DotfileNotFoundError):
            repo.remove(dotdir_file)
