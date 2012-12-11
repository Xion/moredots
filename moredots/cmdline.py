"""
Command line argument parsing.
"""
import os
import argparse

import git


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

    rm_parser = subparsers.add_parser(
        'rm', help="Remove dotfile from repository, "
                   "returning it to home directory in its original state."
    )
    rm_parser.add_argument(
        'filepath',
        metavar="FILE",
        help="Dotfile to remove from repository. Leading dot can be omitted.",
    )
    rm_parser.add_argument(
        'repo',
        type=git_repository,
        metavar="DIRECTORY",
        help="Specify dotfiles repository where the file should be added. "
             "By default, the repository in ~/dotfiles will be used.",
        nargs='?',  # optional
        default=os.path.expanduser('~/dotfiles'),
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
        '--home',
        dest='home_dir',
        metavar="HOME_DIRECTORY",
        help="Specify alternate home directory - that is, the directory where "
             "dotfiles are normally stored. You may want to override this "
             "if you use moredots to manage more than dotfiles repo "
             "on a single machine.",
        default=os.path.expanduser('~/'),
    )

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
