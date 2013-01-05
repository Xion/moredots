"""
Tests for :class:`DotfileRepo` synchronization.
"""
import pytest

from moredots import exc


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
