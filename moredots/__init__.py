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
    repo.index.add(['.mdots/home'])

    # prepare .gitignore
    with open(os.path.join(repo_dir, '.gitignore'), 'w') as f:
        print >>f, '.mdots/home'
    repo.index.add(['.gitignore'])

    repo.index.commit("[moredots] Init dotfiles repository")


def handle_add(repo_dir, filepath, hardlink):
    """Adds a dotfile to dotfiles repository."""
    # TODO: extract this into argparse argument type, so that all functions
    # can already get a git.Repo object instead of just path to repo
    try:
        repo = git.Repo(repo_dir, odbt=git.GitCmdObjectDB)
    except git.InvalidGitRepositoryError:
        print "fatal: %s is not a moredots repository"
        return

    # TODO: add support for files inside dotdirectories, e.g. ~/.config
    _, filename = os.path.split(filepath)
    if filename.startswith('.'):
        filename = filename[1:]
    else:
        # brittle, use os.path functions instead
        filepath = filepath.replace(filename, '.%s' % filename)

    dotfile_in_repo = os.path.join(repo_dir, filename)
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


# Utility functions

def create_argument_parser():
    """Creates argparse command-line parser."""
    parser = argparse.ArgumentParser(
        prog="mdots",
        description="Dotfiles manager based on Git",
        usage="mdots COMMAND [OPTIONS]",
    )
    subparsers = parser.add_subparsers(dest='command')

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
        'repo_dir',
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

    # TODO: add subparsers for rm, install and sync

    return parser
