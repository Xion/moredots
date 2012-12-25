"""
Exception classes used throughout the program.

It is recommended to import this module as a whole (instead of importing
individual exception classes), as it allows to access them all convenientely
and explicitly::

    try:
        # ... some stuff ...
    except exc.DuplicateDotfileError:
        # handle the error
"""


# Dotfile errors

class DotfileError(Exception):
    """Base class for exceptions related to operations on dotfiles."""

    def __init__(self, path, repo=None, *args, **kwargs):
        """Constructor."""
        super(DotfileError, self).__init__(*args, **kwargs)

        self.path = path
        self.repo = repo

    def __repr__(self):
        return "<%s path=%s repo=%s>" % (self.__class__.__name__,
                                         self.path, self.repo)


class DuplicateDotfileError(DotfileError):
    """Error raised when trying to add a dotfile that already exists
    in the dotfiles repository.
    """
    pass


class DotfileNotFoundError(DotfileError):
    """Error raised when tryng to remove a non-exsiting dotfile
    from dotfile repository.
    """
    pass


# Repository errors

class RepositoryError(Exception):
    """Base class for exceptions related to dotfiles repositories as a whole."""

    def __init__(self, repo_dir, *args, **kwargs):
        super(RepositoryError, self).__init__(*args, **kwargs)
        self.repo_dir = repo_dir

    def __repr__(self):
        return "<%s dir=%s>" % (self.__class__.__name__, self.repo_dir)


class RepositoryExistsError(RepositoryError):
    """Error raised when attempting to init or install a dotfile repository
    inside directory where such repo already exists.
    """
    pass


class InvalidHomeDirError(RepositoryError):
    """Error raised when the directory specified as $HOME
    for the dotfile repository is invalid and cannot be used as such.

    This happens e.g. when the directory doesn't exist,
    or is the same as the dotfile repo directory.
    """
    def __init__(self, repo_dir, home_dir, *args, **kwargs):
        super(InvalidHomeDirError, self).__init__(repo_dir, *args, **kwargs)
        self.home_dir = home_dir

    def __repr__(self):
        return "<%s dir=%s home=%s>" % (self.__class__.__name__,
                                        self.repo_dir, self.home_dir)


# Synchronization errors

class SynchronizationError(Exception):
    """Base class for exceptions that may occur during the synchronization
    of dotfile repositories with their remotes.
    """
    def __init__(self, repo, remote=None, *args, **kwargs):
        """Constructor."""
        super(SynchronizationError, self).__init__(*args, **kwargs)

        self.repo = repo
        self.remote = remote

    def __repr__(self):
        return "<%s repo=%s remote=%s>" % (self.__class__.__name__,
                                           self.repo, self.remote)


class NoRemoteError(SynchronizationError):
    """Error raised when no remote dotfile repository has been specified
    while trying to perform synchronization.
    """
    pass


class UnrelatedRemoteError(SynchronizationError):
    """Error raised during synchronization attempt when
    specified remote repository is unrelated to local repository.
    """
    pass
