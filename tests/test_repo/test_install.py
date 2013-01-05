"""
Tests for the :class:`DotfileRepo` installation.
"""
from moredots.repo import DotfileRepo


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
