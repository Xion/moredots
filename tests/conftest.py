"""
Shared utility code for tests.
"""
import os
import random
import string

import pytest

from moredots.repo import DotfileRepo

from tests.utils import random_string


# Directories

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


# Repositories & remotes for them

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
        repo.add(dotfile_in_home(home_dir, dotfile_name()))

    return repo


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


# Dotfiles

@pytest.fixture
def dotfile_in_home(home_dir, dotfile_name):
    """A dotfile inside home directory.
    :return: Path to a dotfile
    """
    path = os.path.join(home_dir, dotfile_name)
    with open(path, 'w') as f:
        print >>f, random_string()
    return path


@pytest.fixture
def dotdir_in_home(home_dir):
    """An empty dot-directory within $HOME dir (.e.g ~/.config/foo).
    Only the first directory has a leading dot.
    """
    path_segments = [home_dir, dotfile_name()]
    path_segments += [filename() for _ in xrange(random.randint(1, 3))]
    path = os.path.join(*path_segments)

    os.makedirs(path)
    return path


@pytest.fixture
def dotdir_file_in_home(dotdir_in_home, filename):
    """A file inside dot-directory within home directory (~/.config/foo/bar).
    :return: Path to a dotfile
    """
    path = os.path.join(dotdir_in_home, filename)
    with open(path, 'w') as f:
        print >>f, random_string()
    return path


@pytest.fixture
def dotfile_name():
    """Random name of a dotfile (without any path fragment)."""
    return "." + random_string(chars=string.ascii_letters, length=16)


@pytest.fixture
def filename():
    """Random file name (without leading dot)."""
    return random_string(chars=string.ascii_letters, length=8)
