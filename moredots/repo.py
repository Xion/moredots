"""
Module containing the :class:`DotfileRepo` class.
"""
import os

import git

from moredots.utils import objectproperty


HOME_FILE = 'mdots_home'
INDEX_FILE = 'mdots_index'

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

    @classmethod
    def init(cls, repo_dir=DEFAULT_REPO_DIR, home_dir=DEFAULT_HOME_DIR):
        """Initializes the dotfiles repository inside given directory.

        :param repo_dir: Directory for the repo. If it exists, it must be empty.
        :param home_dir: Directory to be considered $HOME for the new repo.

        First, a Git repository is created in given path. Then, the moredots
        enhancements are applied, such as saving the home directory.
        """
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

        :return: Whether operation succeeded (boolean value)
        """
        filepath_in_home = os.path.abspath(path)
        relative_filepath = os.path.relpath(filepath_in_home,
                                            start=self.home_dir)

        # check for the file's existence
        filepath_in_repo = os.path.normpath(
            os.path.join(self.dir, relative_filepath))
        if os.path.exists(filepath_in_repo):
            return False

        # perform replacement, producing (sym)link in place of actual file
        link_func = os.link if hardlink else os.symlink
        os.rename(filepath_in_home, filepath_in_repo)
        link_func(filepath_in_repo, filepath_in_home)  # order like shell `ln`

        self._commit(add=relative_filepath)
        return True

    def remove(self, path):
        """Removes dotfile from the dotfile repository.

        :param path: Path to the dotfile inside the repo (either absolute
                     or relative to the repo's working directory)

        :return: Whether operation succeeded (boolean value)
        """
        filepath_in_repo = os.path.abspath(path)
        relative_filepath = os.path.relpath(filepath_in_repo, start=self.dir)

        # check for the links existence and remove it
        # TODO: also check if it's symlink when symlink is expected
        filepath_in_home = os.path.normpath(
            os.path.join(self.home_dir, relative_filepath))
        if os.path.exists(filepath_in_home):
            os.unlink(filepath_in_home)

        # TODO: for hardlinks, we can simply remove the in-repo file
        # instead of removing the home-dir file and doing the rename
        os.rename(filepath_in_repo, filepath_in_home)

        self._commit(remove=relative_filepath)
        return True

    def sync(self, url=None):
        """Synchronizes dotfiles repository with a remote one.

        URL will be set as 'origin' remote for the moredots Git repository.
        In case origin already exists, it will be replaced with one
        pointing to given URL.
        """
        existing_origin = getattr(self.git_repo.remotes, 'origin', None)
        if not (existing_origin or url):
            return False

        if url and existing_origin:
            self.git_repo.delete_remote('origin')
            existing_origin = None

        origin = existing_origin or self.git_repo.create_remote('origin', url)

        # TODO: implement git.RemoteProgress subclass
        # to track progress of long running git operations
        master = self.git_repo.head.ref.name
        try:
            origin.pull(master)  # TODO: merging?...
        except git.GitCommandError:
            pass  # remote doesn't have anything yet - no biggie
        origin.push(master)

        # setting up remote branch tracking for subsequent `mdots sync`
        self.git_repo.head.ref.set_tracking_branch(origin.refs.master)

        self._install_dotfiles()

    @property
    def dir(self):
        """Path to directory where the dotfile repository resides."""
        return self.git_repo.working_dir

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
            home_file = os.path.join(self.git_repo.git_dir, HOME_FILE)
            with open(home_file, 'w') as f:
                print >>f, value

            self._home_dir = value

        return locals()

    # Internal methods

    def _install_dotfiles(self):
        """Install all tracked dotfiles from the repo, (sym)linking
        to them from home directory.
        """
        for directory, subdirs, filenames in os.walk(self.dir):
            for skipdir in ('.git',):
                if skipdir in subdirs:
                    subdirs.remove(skipdir)

            for filename in filenames:
                if filename.startswith('.'):  # these are repo's internal dotfiles,
                    continue                  # such as .gitignore

                # TODO: add support for files inside dot-directories
                repo_path = os.path.join(directory, filename)
                home_path = os.path.join(self.home_dir, '.' + filename)

                if os.path.exists(home_path):
                    os.unlink(home_path)
                os.symlink(repo_path, home_path)  # TODO: support hardlinks

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
        self.git_repo.commit("[moredots] %s" % message.capitalize())
