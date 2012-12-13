"""
Code responsible for handling dotfiles,
especially the links from home directory to
dotfile repository.
"""
import os


def install_dotfiles(repo):
    """Install all tracked dotfiles from given repo, (sym)linking
    to them from home directory.
    """
    home_dir = get_home_dir(repo)

    for directory, subdirs, filenames in os.walk(repo.working_dir):
        for skipdir in ['.git', '.mdots']:
            if skipdir in subdirs:
                subdirs.remove(skipdir)

        for filename in filenames:
            if filename.startswith('.'):  # these are repo's internal dotfiles,
                continue                  # such as .gitignore

            # TODO: add support for files inside dot-directories
            repo_path = os.path.join(directory, filename)
            home_path = os.path.join(home_dir, '.' + filename)

            if os.path.exists(home_path):
                os.unlink(home_path)
            os.symlink(repo_path, home_path)  # TODO: support hardlinks


# Adding and removing files

def move_dotfile_to_repo(filepath, repo, hardlink=False):
    """Moves the dotfile from specified filepath into the dotfile repository.

    :param filepath: Path to the source dotfile. It will be replaced with
                     a (sym)link to the file in repo
    :param repo: :class:`git.Repo` object
    :param hardlink: Whether the file should be hardlinked instead of symlinked.
                     ``False`` by default.

    :return: Whether operation succeeded (boolean value)

    .. note:: This function doesn't touch the repo's index
              and it doesn't commit anything.
    """
    filepath_in_home = os.path.abspath(filepath)

    home_dir = get_home_dir(repo)
    relative_filepath = os.path.relpath(filepath_in_home, start=home_dir)

    # check for the file's existence
    filepath_in_repo = os.path.normpath(
        os.path.join(repo.working_dir, relative_filepath))
    if os.path.exists(filepath_in_repo):
        print "fatal: %s already exists" % filepath_in_repo
        return False

    # perform replacement, producing (sym)link in place of actual file
    link_func = os.link if hardlink else os.symlink
    os.rename(filepath_in_home, filepath_in_repo)
    link_func(filepath_in_repo, filepath_in_home)  # same order as shell's `ln`

    return True


def remove_dotfile_from_repo(filepath, repo):
    """Removes dotfile from the dotfile repository.

    :param filepath: Path to the dotfile inside ``repo`` (either absolute
                     or relative to the repo's working directory)
    :param repo: :class:`git.Repo` object

    :return: Whether operation succeeded (boolean value)
    """
    filepath_in_repo = os.path.abspath(filepath)
    relative_filepath = os.path.relpath(filepath_in_repo,
                                        start=repo.working_dir)

    # check for the links existence and remove it
    # TODO: also check if it's symlink when symlink is expected
    home_dir = get_home_dir(repo)
    filepath_in_home = os.path.normpath(
        os.path.join(home_dir, relative_filepath))
    if os.path.exists(filepath_in_home):
        os.unlink(filepath_in_home)
    else:
        print "warning: %s expected but not found"

    # TODO: for hardlinks, we can simply remove the in-repo file
    # instead of removing the home-dir file and doing the rename
    os.rename(filepath_in_repo, filepath_in_home)
    return True


# Setting and getting home directory for a dotfile repo

def set_home_dir(repo, home_dir):
    """Sets the path for home directory associated with dotfiles repo.

    :param repo: :class:`git.Repo` object
    :param home_dir: Path to home directory
    """
    # make sure .mdots directory exists
    mdots_dir = os.path.join(repo.working_dir, '.mdots')
    try:
        os.mkdir(mdots_dir)
    except OSError, e:
        if getattr(e, 'errno', 0) != 17:  # 17 == directory exists
            raise

    # TODO: store this in `mdots_home` file inside repo `.git` directory
    with open(os.path.join(mdots_dir, 'home'), 'w') as f:
        print >>f, os.path.abspath(home_dir)


def get_home_dir(repo):
    """Retrieves the path for home directory associated with dotfiles repo.
    :param repo: :class:`git.Repo` object
    :return: Path to home directory
    """
    # TODO: would be nice to not do that repeatedly
    # when adding/removing multiple files
    with open(os.path.join(repo.working_dir, '.mdots', 'home')) as f:
        return f.read().strip()
