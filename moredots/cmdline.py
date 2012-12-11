"""
Command line argument parsing.
"""
import os
import argparse

import git


__all__ = ['create_argument_parser']


def create_argument_parser():
    """Creates argparse command-line parser."""
    parser = argparse.ArgumentParser(
        prog="mdots",
        description="Dotfiles manager based on Git",
        usage="mdots COMMAND [OPTIONS]",
    )
    configure_command_subparsers(parser)
    return parser


# Preparing specific commands

def configure_command_subparsers(argparser):
    """Configures the subparses for handling all the moredots commands.
    :param argparser: The :class:`argparse.ArgumentParser` object
    """
    subparsers = argparser.add_subparsers(dest='command')

    configure_init(subparsers)
    configure_add(subparsers)
    configure_rm(subparsers)
    configure_sync(subparsers)
    configure_install(subparsers)


def configure_init(subparsers):
    parser = subparsers.add_parser('init',
                                   help="Initialize dotfiles repository.")

    add_repo_argument(
        parser, existing=False,
        desc="directory where the dotfiles repository should be created")
    parser.add_argument(
        '--home',
        dest='home_dir',
        metavar="HOME_DIRECTORY",
        help="Specify alternate home directory - that is, the directory where "
             "dotfiles are normally stored. You may want to override this "
             "if you use moredots to manage more than dotfiles repo "
             "on a single machine.",
        default=os.path.expanduser('~/'),
    )


def configure_add(subparsers):
    parser = subparsers.add_parser(
        'add', help="Add a dotfile to repository, "
                    "enabling it to be synced across machines.")

    parser.add_argument(
        'filepath',
        metavar="FILE",
        help="Dotfile to add to repository. The leading dot can be omitted.",
    )
    add_repo_argument(parser,
                      desc="dotfiles repository where the file should be added")
    parser.add_argument(
        '--hardlink',
        help="If provided, the dotfile will be hardlinked "
             "rather than symlinked from home directory.",
        action='store_true',
        default=False,
    )


def configure_rm(subparsers):
    parser = subparsers.add_parser(
        'rm', help="Remove dotfile from repository, "
                   "returning it to home directory in its original state.")

    parser.add_argument(
        'filepath',
        metavar="FILE",
        help="Dotfile to remove from repository. Leading dot can be omitted.",
    )
    add_repo_argument(
        parser, desc="dotfiles repository that the file should be removed from")


def configure_sync(subparsers):
    parser = subparsers.add_parser(
        'sync', help="Synchronize local dotfiles repository with remote one.")

    parser.add_argument(
        'remote_url',
        metavar="REMOTE_URL",
        help="Specify URL to remote dotfiles repository which should be synced.",
        nargs='?',  # optional
        default=None,
    )
    add_repo_argument(
        parser, desc="local dotfiles repository to be synced with remote one")


def configure_install(subparsers):
    parser = subparsers.add_parser(
        'install', help="Installs dotfiles from a remote repository.")

    parser.add_argument(
        'remote_url',
        metavar="REMOTE_URL",
        help="Specify URL to remote dotfiles repository to be installed.",
    )
    add_repo_argument(parser, existing=False,
                      desc="directory for the local dotfiles repository")
    parser.add_argument(
        '--home',
        dest='home_dir',
        metavar="HOME_DIRECTORY",
        help="Specify alternate home directory - that is, the directory where "
             "dotfiles are normally stored. You may want to override this "
             "if you use moredots to manage more than dotfiles repo "
             "on a single machine.",
        default=os.path.expanduser('~/'),
    )


# Common parameters

def add_repo_argument(parser, *args, **kwargs):
    """Include the argument representing local moredots repository.

    :param existing: Whether the repo is expected to existing or not.
                     Must be supplied as keyword. ``True`` by default.
    :param desc: Description of the repo argument, which can be somewhat
                 specific to particular command. Must be supplied as keyword.

    Depending on what parameters this function receives, the argument can be
    made into positional one or a flag. The former is the default, though.
    """
    args = args or ('repo',)
    desc = kwargs.pop('desc', "local dotfiles repository")
    existing = kwargs.pop('existing', True)

    # prepare keyword arguments dict
    help_text = (
        "By default, the repository in ~/dotfiles will be used."
        if existing else "By default, it will be placed in ~/dotfiles.")
    kwargs.update(
        metavar="DIRECTORY",
        help="Specify %s. %s" % (desc, help_text),
        nargs='?',  # optional
        default=os.path.expanduser('~/dotfiles'),
    )
    if existing:
        kwargs['type'] = git_repository

    parser.add_argument(*args, **kwargs)


# Utility functions

def git_repository(repo_dir):
    """argparse argument type for converting paths to Git repositories
    into :class:`git.Repo` objects automatically.
    """
    try:
        return git.Repo(repo_dir, odbt=git.GitCmdObjectDB)
    except git.InvalidGitRepositoryError:
        msg = "fatal: %s is not a moredots repository" % repo_dir
        raise argparse.ArgumentError(msg)
