"""
Package with tests for the :class:`DotfileRepo` class.
"""
import os


def dotfile_exists(dotfile_in_home, repo):
    """Checks that dotfile with given $HOME path exists
    in given dotfile repository.

    .. note:: This doesn't work for files in dot-directories,
              use :func:`dotdir_file_exists` instead
    """
    _, name = os.path.split(dotfile_in_home)
    return os.path.exists(os.path.join(repo.dir, name[1:]))


def dotdir_file_exists(dotdir_file_in_home, home_dir, repo):
    """Checks that files inside dot-directory with given $HOME path
    exists in given dotfile repository.
    """
    dotdir_file = os.path.relpath(dotdir_file_in_home, start=home_dir)
    return os.path.exists(os.path.join(repo.dir, dotdir_file[1:]))
