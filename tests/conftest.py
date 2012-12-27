"""
Shared utility code for tests.
"""
import os
import random
import string

import git

import pytest

from moredots.repo import DotfileRepo

from tests.utils import random_string


# Fixtures / resources

@pytest.fixture
def git_repo(tmpdir):
    """Provides a local Git repository, created in a temporary directory."""
    return git.Repo.init(str(tmpdir))


@pytest.fixture
def repo_dir(tmpdir):
    """Directory to place the dotfile repo in."""
    return str(tmpdir.mkdir('repo'))


@pytest.fixture
def home_dir(tmpdir):
    """Directory to act as $HOME for the dotfile repo."""
    return str(tmpdir.mkdir('home'))


@pytest.fixture
def remote_dir(tmpdir):
    """Directory for "remote" dotfiles repository."""
    return str(tmpdir.mkdir('remote'))


@pytest.fixture
def empty_repo(repo_dir, home_dir):
    """Empty moredots repository."""
    return DotfileRepo.init(repo_dir, home_dir)


@pytest.fixture
def filled_repo(repo_dir, home_dir):
    """Moredots repository with at least one dotfile."""
    repo = DotfileRepo.init(repo_dir, home_dir)

    # add some dotfiles
    for _ in xrange(random.randint(1, 5)):
        repo.add(dotfile(home_dir, dotfile_name()))

    return repo


@pytest.fixture
def dotfile(home_dir, dotfile_name):
    """A dotfile inside home directory.
    :return: Name of a dotfile
    """
    path = os.path.join(home_dir, dotfile_name)
    with open(path, 'w') as f:
        print >>f, random_string()
    return path


@pytest.fixture
def dotfile_name():
    """Random name of a dotfile."""
    return "." + random_string(chars=string.ascii_letters, length=16)
