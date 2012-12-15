"""
Unit tests for command line parser.
"""
from moredots.cmdline import create_argument_parser

import pytest


# Tests

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


# Fixtures / resources

@pytest.fixture
def argparser():
    """Provide :class:`argparse.ArgumentParser` for use by tests."""
    return create_argument_parser()
