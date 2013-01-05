"""
Tests for the :class:`DotfileRepo` initialization.
"""
import pytest

from moredots import exc
from moredots.repo import DotfileRepo


class TestInit(object):

    def test_init_basics(self, repo_dir, home_dir):
        repo = DotfileRepo.init(repo_dir, home_dir)
        assert repo.dir == repo_dir
        assert repo.home_dir == home_dir

    def test_init_persists_home_dir(self, repo_dir, home_dir):
        repo1 = DotfileRepo.init(repo_dir, home_dir)
        repo2 = DotfileRepo(repo_dir)  # from existing repo
        assert repo1.home_dir == repo2.home_dir

    def test_init_in_invalid_home_dir(self, repo_dir):
        with pytest.raises(exc.InvalidHomeDirError):
            DotfileRepo.init(repo_dir, home_dir=repo_dir)

    def test_init_in_existing_repo(self, empty_repo):
        with pytest.raises(exc.RepositoryExistsError):
            DotfileRepo.init(empty_repo.dir)
