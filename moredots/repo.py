"""
Module containing the :class:`DotfileRepo` class.
"""
import os

import git

from moredots import exc
from moredots.inventory import Inventory
from moredots.utils import objectproperty, remove_dot, restore_dot


__all__ = ['DotfileRepo']


HOME_FILE = 'mdots_home'

DEFAULT_REPO_DIR = os.path.expanduser('~/dotfiles')
DEFAULT_HOME_DIR = os.path.expanduser('~/')


class DotfileRepo(object):
    """Represents the local repository of dotfiles.

    A dotfile repo is a thin layer upon the normal Git repository,
    along with some moredots-specific data files and logic.
    """
    def __init__(self, repo):
        """Constructor.

        :param repo: Path to the dotfiles repository or a :class:`git.Repo`
                     object representing the Git repo with moredots enhancements
        """
        if isinstance(repo, basestring):
            repo = git.Repo(repo, odbt=git.GitCmdObjectDB)

        self.git_repo = repo
        self.inventory = Inventory(self)

    def __repr__(self):
        """Textual representation of repo object."""
        return "<%s at %s linked from %s>" % (self.__class__.__name__,
                                              self.dir, self.home_dir)

    @classmethod
    def init(cls, repo_dir=DEFAULT_REPO_DIR, home_dir=DEFAULT_HOME_DIR):
        """Initializes the dotfiles repository inside given directory.

        :param repo_dir: Directory for the repo. If it exists, it must be empty.
        :param home_dir: Directory to be considered $HOME for the new repo.

        First, a Git repository is created in given path. Then, the moredots
        enhancements are applied, such as saving the home directory.
        """
        cls._check_dirs(repo_dir, home_dir)

        repo = cls(git.Repo.init(repo_dir, mkdir=True))
        repo.home_dir = home_dir
        return repo

    @classmethod
    def install(cls, url, repo_dir=DEFAULT_REPO_DIR, home_dir=DEFAULT_HOME_DIR):
        """Installs remote dotfile repository on this machine.

        :param url: URL to the remote repository which will be git-clone'd.
        :param repo_dir: Directory for the repo. If it exists, it must be empty.
        :param home_dir: Driectory to be considered $HOME for the new repo.
        """
        cls._check_dirs(repo_dir, home_dir)

        repo = cls(git.Repo.clone_from(url, repo_dir))
        repo.home_dir = home_dir
        repo._install_dotfiles()

        return repo

    def add(self, path, hardlink=False):
        """Moves the dotfile from specified filepath into the dotfile repository.

        :param path: Path to the source dotfile. It will be replaced with
                     a (sym)link to the file in repo
        :param hardlink: Whether the file should be hardlinked
                         instead of symlinked. ``False`` by default.

        :raise: ``exc.DuplicateDotfileError`` if the file already exists
        """
        path_in_home, path_in_repo = self._filepath_pair(path)
        relative_filepath = os.path.relpath(path_in_home, start=self.home_dir)

        if os.path.exists(path_in_repo):
            raise exc.DuplicateDotfileError(relative_filepath, repo=self)

        # perform replacement, producing (sym)link in place of actual file
        link_func = os.link if hardlink else os.symlink
        os.rename(path_in_home, path_in_repo)
        link_func(path_in_repo, path_in_home)  # order like shell `ln`

        with self.inventory as inv:
            inv.add(path_in_repo, hardlink=hardlink)

        self._commit("add %s" % relative_filepath, add=path_in_repo)

    def remove(self, path):
        """Removes dotfile from the dotfile repository.

        :param path: Path to the dotfile inside the repo (either absolute
                     or relative to the repo's working directory)

        :raise: ``exc.DotfileNotFoundError`` if dotfile is not in the repo
        """
        path_in_home, path_in_repo = self._filepath_pair(path)
        relative_filepath = os.path.relpath(path_in_home, start=self.home_dir)

        if not os.path.exists(path_in_repo):
            raise exc.DotfileNotFoundError(relative_filepath, repo=self)

        # restore the dotfile back into $HOME directory
        if os.path.exists(path_in_home):
            os.unlink(path_in_home)  # TODO: also check if it's symlink
                                     # when symlink is expected
        os.rename(path_in_repo, path_in_home)

        with self.inventory as inv:
            inv.remove(path_in_repo)

        self._commit("remove %s" % relative_filepath, remove=path_in_repo)

    def sync(self, url=None):
        """Synchronizes dotfiles repository with a remote one.

        URL will be set as 'origin' remote for the moredots Git repository.
        In case origin already exists, it will be replaced with one
        pointing to given URL.
        """
        existing_origin = getattr(self.git_repo.remotes, 'origin', None)
        if not (existing_origin or url):
            raise exc.NoRemoteError(repo=self)

        if url and existing_origin:
            self.git_repo.delete_remote('origin')
            existing_origin = None

        origin = existing_origin or self.git_repo.create_remote('origin', url)

        # TODO: implement git.RemoteProgress subclass
        # to track progress of long running git operations
        master = self.git_repo.head.ref.name
        try:
            origin.pull(master)  # TODO: merging?...
            was_empty = False
        except git.GitCommandError:
            was_empty = True  # remote has nothing yet, so we just push
        origin.push(master)

        if was_empty:
            return

        # check if we actually pulled something for the specified remote
        origin_refs = list(git.refs.remote.RemoteReference.iter_items(
            self.git_repo, remote=origin))
        if not origin_refs:
            raise exc.UnrelatedRemoteError(repo=self, remote=origin)

        # set up remote branch tracking for subsequent `mdots sync`
        self.git_repo.head.ref.set_tracking_branch(origin.refs.master)

        self.inventory.load()
        self._install_dotfiles()

    @property
    def dir(self):
        """Path to directory where the dotfile repository resides."""
        return self.git_repo.working_dir

    @property
    def dotfiles(self):
        """Iterable of absolute paths to all dotfiles
        stored within this repository.
        """
        for directory, subdirs, filenames in os.walk(self.dir):
            for skipdir in ('.git',):
                if skipdir in subdirs:
                    subdirs.remove(skipdir)

            for filename in filenames:
                if filename.startswith('.'):  # these are repo's own dotfiles,
                    continue                  # such as .gitignore

                yield os.path.join(directory, filename)

    @objectproperty
    def home_dir():
        """Path to directory which is considered "home" (or $HOME)
        for this dotfiles repository.

        A home directory is the one where the dotfiles normally reside,
        and from which we're (sym)linking to the files inside our repo.
        """
        def get(self):
            home_dir = getattr(self, '_home_dir', None)
            if not home_dir:
                home_file = os.path.join(self.git_repo.git_dir, HOME_FILE)
                with open(home_file, 'r') as f:
                    home_dir = self._home_dir = f.read().strip()

            return home_dir

        def set(self, value):
            if value == self.dir:
                raise ValueError(
                    "home directory cannot be equal to repo directory")

            home_file = os.path.join(self.git_repo.git_dir, HOME_FILE)
            with open(home_file, 'w') as f:
                print >>f, value

            self._home_dir = value

        return locals()

    @property
    def is_valid(self):
        """Whether repository is a valid one, i.e. contains all the necessary
        files and information.
        """
        home_file = os.path.join(self.dir, HOME_FILE)
        return all([git.repo.fun.is_git_dir(self.git_repo.git_dir),
                    os.path.exists(home_file)])

    # Internal methods

    @classmethod
    def _check_dirs(cls, repo_dir, home_dir):
        """Check given directories - for repository and the $HOME dir to be
        linked with it - to see if they are fullfil necessary requirements.

        :raise: Various exceptions if directories do not conform
        """
        if os.path.isdir(repo_dir) and len(os.listdir(repo_dir)) > 0:
            raise exc.RepositoryExistsError(repo_dir)

        home_dir_exists = os.path.exists(home_dir) and os.path.isdir(home_dir)
        if not home_dir_exists or home_dir == repo_dir:
            raise exc.InvalidHomeDirError(repo_dir, home_dir)

    def _install_dotfiles(self):
        """Install all tracked dotfiles from the repo, (sym)linking
        to them from home directory.
        """
        for filepath in self.dotfiles:
            home_path, repo_path = self._filepath_pair(filepath)

            if os.path.exists(home_path):
                os.unlink(home_path)
            os.symlink(repo_path, home_path)  # TODO: support hardlinks

    def _filepath_pair(self, filepath):
        """Given a path to a dotfile, returns a pair of paths to this dotfile
        both inside repo's $HOME directory and the repo itself.

        :param filepath: Either of the two (absolute) paths or equivalent
                         relative path

        :return: Pair of absolute paths: (dotfile_in_home, dotfile_in_repo)

        .. note;: Existence of either of files involved is not checked.
        """
        if not filepath:
            raise ValueError("empty dotfile path")

        # case 1: relative path
        if not os.path.isabs(filepath):
            in_home = os.path.join(self.home_dir, filepath)
            in_repo = os.path.join(self.dir, remove_dot(filepath))
            return in_home, in_repo

        # case 2: absolute path inside $HOME
        if os.path.commonprefix([filepath, self.home_dir]) == self.home_dir:
            relative_path = os.path.relpath(filepath, start=self.home_dir)
            in_home = filepath
            in_repo = os.path.join(self.dir, remove_dot(relative_path))
            return in_home, in_repo

        # case 3: absolute path inside repo's directory
        if os.path.commonprefix([filepath, self.dir]) == self.dir:
            relative_path = restore_dot(os.path.relpath(filepath,
                                                        start=self.dir))
            in_home = os.path.join(self.home_dir, relative_path)
            in_repo = filepath
            return in_home, in_repo

        raise ValueError("invalid dotfile path")

    def _commit(self, message=None, add=None, remove=None):
        """Commits files to the dotfile Git repository.

        :param message: Commit message.
                        If omitted, it is constructed based on changed files.
        :param add: Files to be added with the commit
        :param remove: Files to be removed with the commit
        """
        if not (add or remove):
            return

        # modify Git index for the repo, handling given paths smartly
        def convert_path(path):
            return (os.path.relpath(path, start=self.dir)
                    if os.path.isabs(path) else path)
        if add:
            add = [add] if isinstance(add, basestring) else add
            self.git_repo.index.add(map(convert_path, add))
        if remove:
            remove = [remove] if isinstance(remove, basestring) else remove
            self.git_repo.index.remove(map(convert_path, remove))

        message = message or "; ".join(filter(None, (
            "add %s" % ", ".join(add) if add else "",
            "remove %s" % ", ".join(remove) if remove else "",
        )))
        self.git_repo.index.commit("[moredots] %s" % message.capitalize())
