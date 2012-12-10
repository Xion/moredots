"""
moredots -- root file
:author: Karol Kuczmarski "Xion"
"""
import os
import argparse

import git


def main():
    """Entry point."""
    parser = create_argument_parser()
    args = vars(parser.parse_args())

    # dispatch execution depending on what command was issued
    command = args.pop('command', None)
    if command:
        command_handler = globals()['handle_%s' % command]
        return command_handler(**args)


# Handlers for different commands

def handle_init(repo_dir, home_dir):
    """Initialize dotfiles repository."""
    repo_gitdir = os.path.join(repo_dir, '.git')
    if git.repo.fun.is_git_dir(repo_gitdir):
        print "fatal: %s is already a Git repository" % repo_dir
        return

    repo = git.Repo.init(repo_dir, mkdir=True)

    # create .mdots directory and put necessary stuff there
    mdots_dir = os.path.join(repo_dir, '.mdots')
    os.mkdir(mdots_dir)
    with open(os.path.join(mdots_dir, 'home'), 'w') as f:
        print >>f, home_dir

    # prepare .gitignore
    with open(os.path.join(repo_dir, '.gitignore'), 'w') as f:
        print >>f, '.mdots/home'
    repo.index.add(['.gitignore'])

    repo.index.commit("[moredots] Init dotfiles repository")


def handle_add(repo, filepath, hardlink):
    """Adds a dotfile to dotfiles repository."""

    # TODO: add support for files inside dotdirectories, e.g. ~/.config
    _, filename = os.path.split(filepath)
    if filename.startswith('.'):
        filename = filename[1:]
    else:
        # TODO: this is brittle, use os.path functions instead
        filepath = filepath.replace(filename, '.%s' % filename)

    dotfile_in_repo = os.path.join(repo.working_dir, filename)
    if os.path.exists(dotfile_in_repo):
        print "fatal: %s already exists" % dotfile_in_repo
        return

    # replace original dotfile with (sym)link
    link_func = os.link if hardlink else os.symlink
    os.rename(filepath, dotfile_in_repo)
    link_func(dotfile_in_repo, filepath)

    # commit changes
    repo.index.add([filename])
    repo.index.commit("[moredots] Add .%s" % filename)


def handle_sync(repo, remote_url):
    """Synchronizes dotfiles repository with a remote one.

    URL will be set as 'origin' remote for the moredots Git repository.
    In case origin already exists, it will be replaced with one
    pointing to given URL.
    """
    existing_origin = getattr(repo.remotes, 'origin', None)
    if not (existing_origin or remote_url):
        print "fatal: no remote repository to sync with"
        return

    if remote_url and existing_origin:
        repo.delete_remote('origin')
        existing_origin = None

    origin = existing_origin or repo.create_remote('origin', remote_url)

    # TODO: implement git.RemoteProgress subclass
    # to track progress of long running git operations
    master = repo.head.ref.name
    try:
        origin.pull(master)  # TODO: merging?...
    except git.GitCommandError:
        pass  # remote doesn't have anything yet - no biggie
    origin.push(master)

    # setting up remote branch tracking for user's convenience
    repo.head.ref.set_tracking_branch(origin.refs.master)


def handle_install(remote_url, repo_dir, home_dir):
    """Installs remote dotfiles repository on this machine."""
    repo_gitdir = os.path.join(repo_dir, '.git')
    if git.repo.fun.is_git_dir(repo_gitdir):
        print "fatal: %s is already a Git repository" % repo_dir
        return

    # TODO: implement progress tracking for this operation
    git.Repo.clone_from(remote_url, repo_dir)

    # create .mdots directory and put necessary stuff there
    # TODO: this is duplicated from handle_init, move to separate function
    mdots_dir = os.path.join(repo_dir, '.mdots')
    os.mkdir(mdots_dir)
    with open(os.path.join(mdots_dir, 'home'), 'w') as f:
        print >>f, home_dir

    # (sym)link dotfiles from the repo to home directory
    for directory, subdirs, filenames in os.walk(repo_dir):
        for skipdir in ['.git', '.mdots']:
            if skipdir in subdirs:
                subdirs.remove(skipdir)
        for filename in filenames:
            # TODO: add support for files inside dot-directories
            repo_path = os.path.join(repo_dir, directory, filename)
            home_path = os.path.join(home_dir, directory, '.' + filename)

            if os.path.exists(home_path):
                os.unlink(home_path)
            os.symlink(repo_path, home_path)  # TODO: support hardlinks


# Utility functions

def create_argument_parser():
    """Creates argparse command-line parser."""
    parser = argparse.ArgumentParser(
        prog="mdots",
        description="Dotfiles manager based on Git",
        usage="mdots COMMAND [OPTIONS]",
    )
    subparsers = parser.add_subparsers(dest='command')

    # TODO: reduce obvious (and non-obvious) duplications in the code below

    init_parser = subparsers.add_parser('init',
                                        help="Initialize dotfiles repository.")
    init_parser.add_argument(
        'repo_dir',
        metavar="DIRECTORY",
        help="Specify directory where the dotfiles repository "
             "should be created. By default, ~/dotfiles will be used. "
             "If directory path doesn't exist, it will be created.",
        nargs='?',  # optional
        default=os.path.expanduser('~/dotfiles'),
    )
    init_parser.add_argument(
        '--home',
        dest='home_dir',
        metavar="HOME_DIRECTORY",
        help="Specify alternate home directory - that is, the directory where "
             "dotfiles are normally stored. You may want to override this "
             "if you use moredots to manage more than dotfiles repo "
             "on a single machine.",
        default=os.path.expanduser('~/'),
    )

    add_parser = subparsers.add_parser(
        'add', help="Add a dotfile to repository, "
                    "enabling it to be synced across machines.")
    add_parser.add_argument(
        'filepath',
        metavar="FILE",
        help="Dotfile to add to repository. The leading dot can be omitted.",
    )
    add_parser.add_argument(
        'repo',
        type=git_repository,
        metavar="DIRECTORY",
        help="Specify dotfiles repository where the file should be added. "
             "By default, the repository in ~/dotfiles will be used.",
        nargs='?',  # optional
        default=os.path.expanduser('~/dotfiles'),
    )
    add_parser.add_argument(
        '--hardlink',
        help="If provided, the dotfile will be hardlinked "
             "rather than symlinked from home directory.",
        action='store_true',
        default=False,
    )

    sync_parser = subparsers.add_parser(
        'sync', help="Synchronize local dotfiles repository with remote one.")
    sync_parser.add_argument(
        'remote_url',
        metavar="REMOTE_URL",
        help="Specify URL to remote dotfiles repository which should be synced.",
        nargs='?',  # optional
        default=None,
    )
    sync_parser.add_argument(
        'repo',
        type=git_repository,
        metavar="DIRECTORY",
        help="Specify local dotfiles repository to be synced with remote one. "
             "By default, the repository in ~/dotfiles will be used.",
        nargs='?',  # optional
        default=os.path.expanduser('~/dotfiles'),
    )

    install_parser = subparsers.add_parser(
        'install', help="Installs dotfiles from a remote repository.")
    install_parser.add_argument(
        'remote_url',
        metavar="REMOTE_URL",
        help="Specify URL to remote dotfiles repository to be installed.",
    )
    install_parser.add_argument(
        'repo_dir',
        metavar="DIRECTORY",
        help="Specify directory for the local dotfiles repository."
             "By default, it will be placed in ~/dotfiles.",
        nargs='?',  # optional
        default=os.path.expanduser('~/dotfiles'),
    )
    install_parser.add_argument(
        'home_dir',
        metavar="HOME_DIRECTORY",
        help="Specify alternate home directory - that is, the directory where "
             "dotfiles are normally stored. You may want to override this "
             "if you use moredots to manage more than dotfiles repo "
             "on a single machine.",
        nargs='?',  # optional
        default=os.path.expanduser('~/'),
    )

    # TODO: add subparser for rm

    return parser


def git_repository(repo_dir):
    """argparse argument type for converting paths to Git repositories
    into :class:`git.Repo` objects automatically.
    """
    try:
        return git.Repo(repo_dir, odbt=git.GitCmdObjectDB)
    except git.InvalidGitRepositoryError:
        msg = "fatal: %s is not a moredots repository" % repo_dir
        raise argparse.ArgumentError(msg)
