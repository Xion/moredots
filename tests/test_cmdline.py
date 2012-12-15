"""
Unit tests for command line parser.
"""
import git

from moredots.cmdline import create_argument_parser

import pytest


# Tests

class TestAdd(object):

    FILEPATH = "./.foobar"

    def test_without_args(self, argparser):
        with pytest.raises(SystemExit):
            argparser.parse_args(['add'])

    def test_with_filepath_arg(self, argparser):
        args = argparser.parse_args(['add', self.FILEPATH])
        assert args.filepath == self.FILEPATH
        assert not args.hardlink

    def test_with_filepath_and_repo_arg(self, argparser, git_repo):
        args = argparser.parse_args([
            'add', self.FILEPATH, git_repo.working_dir])

        assert args.filepath == self.FILEPATH
        assert args.repo.working_dir == git_repo.working_dir
        assert not args.hardlink

    def test_with_filepath_and_hardlink_arg(self, argparser):
        args = argparser.parse_args(['add', self.FILEPATH, '--hardlink'])
        assert args.filepath == self.FILEPATH
        assert args.hardlink

    def test_with_all_args(self, argparser, git_repo):
        args = argparser.parse_args([
            'add', self.FILEPATH, git_repo.working_dir, '--hardlink'])

        assert args.filepath == self.FILEPATH
        assert args.repo.working_dir == git_repo.working_dir
        assert args.hardlink


class TestInit(object):

    REPO_DIR = "./foo/bar"
    HOME_DIR = "./baz/qux"

    def test_without_args(self, argparser):
        argparser.parse_args(['init'])

    def test_with_repo_arg(self, argparser):
        args = argparser.parse_args(['init', self.REPO_DIR])
        assert args.repo_dir == self.REPO_DIR

    def test_with_all_args(self, argparser):
        args = argparser.parse_args([
            'init', self.REPO_DIR, '--home', self.HOME_DIR])

        assert args.repo_dir == self.REPO_DIR
        assert args.home_dir == self.HOME_DIR


class TestInstall(object):

    URL = "file:///tmp/foo"
    REPO_DIR = "./foo/bar"
    HOME_DIR = "./baz/qux"

    def test_without_args(self, argparser):
        with pytest.raises(SystemExit):
            argparser.parse_args(['install'])

    def test_with_url_arg(self, argparser):
        args = argparser.parse_args(['install', self.URL])
        assert args.remote_url == self.URL

    def test_with_url_and_repo_args(self, argparser):
        args = argparser.parse_args(['install', self.URL, self.REPO_DIR])
        assert args.remote_url == self.URL
        assert args.repo_dir == self.REPO_DIR

    def test_with_url_and_home_args(self, argparser):
        args = argparser.parse_args([
            'install', self.URL, '--home', self.HOME_DIR])

        assert args.remote_url == self.URL
        assert args.home_dir == self.HOME_DIR

    def test_with_all_args(self, argparser):
        args = argparser.parse_args(['install', self.URL, self.REPO_DIR,
                                     '--home', self.HOME_DIR])

        assert args.remote_url == self.URL
        assert args.repo_dir == self.REPO_DIR
        assert args.home_dir == self.HOME_DIR


class TestRm(object):

    FILEPATH = "./.foobar"

    def test_without_args(self, argparser):
        with pytest.raises(SystemExit):
            argparser.parse_args(['rm'])

    def test_with_filepath_arg(self, argparser):
        args = argparser.parse_args(['rm', self.FILEPATH])
        assert args.filepath == self.FILEPATH

    def test_with_all_args(self, argparser, git_repo):
        args = argparser.parse_args(['rm', self.FILEPATH, git_repo.working_dir])
        assert args.filepath == self.FILEPATH
        assert args.repo.working_dir == git_repo.working_dir


# Fixtures / resources

@pytest.fixture
def argparser():
    """Provide :class:`argparse.ArgumentParser` for use by tests."""
    return create_argument_parser()


@pytest.fixture
def git_repo(tmpdir):
    """Provides a local Git repository, created in a temporary directory."""
    return git.Repo.init(str(tmpdir))
