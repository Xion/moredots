"""
Tests for the :class:`DotfileRepo` class.
"""
import os

import pytest

from moredots import exc
from moredots.repo import DotfileRepo

from tests.conftest import empty_repo, filled_repo


# Tests

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


class TestInstall(object):

    def test_install_basics(self, empty_remote_url, repo_dir, home_dir):
        repo = DotfileRepo.install(empty_remote_url, repo_dir, home_dir)
        assert repo.dir == repo_dir
        assert repo.home_dir == home_dir

    def test_install_adds_git_remote(self, filled_remote_url, repo_dir, home_dir):
        repo = DotfileRepo.install(filled_remote_url, repo_dir, home_dir)
        origin = repo.git_repo.remotes.origin
        assert origin.url == filled_remote_url
        assert len(origin.refs) > 0

    def test_install_empty(self, empty_remote_url, repo_dir, home_dir):
        repo = DotfileRepo.install(empty_remote_url, repo_dir, home_dir)
        assert len(list(repo.dotfiles)) == 0

    def test_install_filled(self, filled_remote_url, repo_dir, home_dir):
        repo = DotfileRepo.install(filled_remote_url, repo_dir, home_dir)
        assert len(list(repo.dotfiles)) > 0


class TestAdd(object):

    def test_add_file_to_empty(self, empty_repo, dotfile):
        repo = empty_repo
        repo.add(dotfile)

        _, name = os.path.split(dotfile)
        assert os.path.exists(os.path.join(repo.dir, name[1:]))

    def test_add_file_to_nonempty(self, filled_repo, dotfile):
        repo = filled_repo
        repo.add(dotfile)

        _, name = os.path.split(dotfile)
        assert os.path.exists(os.path.join(repo.dir, name[1:]))

    def test_add_existing_file(self, empty_repo, dotfile):
        repo = empty_repo
        repo.add(dotfile)

        with pytest.raises(exc.DuplicateDotfileError):
            repo.add(dotfile)


class TestRemove(object):

    def test_remove_existing_file(self, filled_repo):
        repo = filled_repo

        dotfile = next(repo.dotfiles)
        repo.remove(dotfile)

        _, name = os.path.split(dotfile)
        assert not os.path.exists(os.path.join(repo.dir, name[1:]))

    def test_remove_nonexistent_file(self, filled_repo):
        repo = filled_repo

        dotfile = next(repo.dotfiles) + '_does_not_exist'
        with pytest.raises(exc.DotfileNotFoundError):
            repo.remove(dotfile)

    def test_remove_same_file_twice(self, filled_repo):
        repo = filled_repo
        dotfile = next(repo.dotfiles)

        repo.remove(dotfile)
        with pytest.raises(exc.DotfileNotFoundError):
            repo.remove(dotfile)


def test_add_and_remove_file(empty_repo, dotfile):
    repo = empty_repo
    repo.add(dotfile)
    repo.remove(dotfile)

    _, name = os.path.split(dotfile)
    assert not os.path.exists(os.path.join(repo.dir, name[1:]))


class TestSync(object):

    def test_sync_empty_with_nothing(self, empty_repo):
        # no remote repo to sync with
        with pytest.raises(exc.NoRemoteError):
            empty_repo.sync()

    def test_sync_empty_with_empty_remote(self, empty_repo, empty_remote_url):
        repo = empty_repo
        count_before = len(list(repo.dotfiles))
        repo.sync(empty_remote_url)
        count_after = len(list(repo.dotfiles))

        assert count_before == count_after == 0

    def test_sync_empty_with_filled_remote(self, empty_repo, filled_remote_url):
        repo = empty_repo
        repo.sync(filled_remote_url)
        assert len(list(repo.dotfiles)) > 0

    def test_sync_filled_with_empty_remote(self, filled_repo, empty_remote_url):
        repo = filled_repo
        count_before = len(list(repo.dotfiles))
        repo.sync(empty_remote_url)
        count_after = len(list(repo.dotfiles))

        assert count_before == count_after

    def test_sync_with_unrelated_remote(self, filled_repo, filled_remote_url):
        with pytest.raises(exc.UnrelatedRemoteError):
            filled_repo.sync(filled_remote_url)


# Fixtures / resources

@pytest.fixture
def empty_remote_url(remote_dir, home_dir):
    """Empty dotfiles repository to act as remote,
    to install from or sync with it.
    """
    # home_dir doesn't matter, it can be the same as the one for "local"
    # repo because the "remote" one is not using it at all
    repo = empty_repo(remote_dir, home_dir)
    return 'file://' + repo.dir


@pytest.fixture
def filled_remote_url(remote_dir, home_dir):
    """Moredots repository with at least one dotfile
    that can act as remote, to install from or sync with it.
    """
    # see the comment about home_dir above
    repo = filled_repo(remote_dir, home_dir)
    return 'file://' + repo.dir
