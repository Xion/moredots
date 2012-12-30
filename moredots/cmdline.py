"""
Command line argument parsing.
"""
import os
import argparse

import git

from moredots.repo import DotfileRepo


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
    """Configure command used to initialize an empty dotfiles repository."""
    parser = subparsers.add_parser('init',
                                   help="Initialize dotfiles repository.")

    add_repo_argument(
        parser, existing=False,
        desc="directory where the dotfiles repository should be created")
    add_home_dir_argument(parser)


def configure_add(subparsers):
    """Configure command used to add a dotfile to dotfiles repository."""
    parser = subparsers.add_parser(
        'add', help="Add a dotfile to repository, "
                    "enabling it to be synced across machines.")

    add_filepath_argument(parser, purpose="add to repository")
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
    """Configure command used to remove a dotfile from dotfiles repository."""
    parser = subparsers.add_parser(
        'rm', help="Remove dotfile from repository, "
                   "returning it to home directory in its original state.")

    add_filepath_argument(parser, purpose="remove from repository")
    add_repo_argument(
        parser, desc="dotfiles repository that the file should be removed from")


def configure_sync(subparsers):
    """Configure command used to synchronize with remote dotfiles repository."""
    parser = subparsers.add_parser(
        'sync', help="Synchronize local dotfiles repository with remote one.")

    add_remote_url_argument(parser, required=False,
                            desc="remote dotfiles repository to sync with")
    add_repo_argument(
        parser, desc="local dotfiles repository to be synced with remote one")


def configure_install(subparsers):
    """Configure command used to 'install' (clone & symlink files)
    a remote dotfiles repository.
    """
    parser = subparsers.add_parser(
        'install', help="Installs dotfiles from a remote repository.")

    add_remote_url_argument(parser, required=True,
                            desc="remote dotfiles repository to install")
    add_repo_argument(parser, existing=False,
                      desc="directory for the local dotfiles repository")
    add_home_dir_argument(parser)


# Common parameters

def add_repo_argument(parser, *args, **kwargs):
    """Include the argument representing local moredots repository.

    :param existing: Whether the repo is expected to exist or not.
                     Must be supplied as keyword. ``True`` by default.
    :param desc: Description of the repo argument, which can be somewhat
                 specific to particular command. Must be supplied as keyword.

    Depending on what parameters this function receives, the argument can be
    made into positional one or a flag. The former is the default, though.
    """
    desc = kwargs.pop('desc', "local dotfiles repository")
    existing = kwargs.pop('existing', True)

    args = args or ['repo' if existing else 'repo_dir']

    # prepare keyword arguments dict
    help_text = (
        "By default, the repository in ~/dotfiles will be used."
        if existing else "By default, it will be placed in ~/dotfiles.")
    arg_type = dotfile_repo if existing else str
    kwargs.update(
        type=arg_type,
        metavar="DIRECTORY",
        help="Specify %s. %s" % (desc, help_text),
        nargs='?',  # optional
        default=arg_type(os.path.expanduser('~/dotfiles')),
    )

    parser.add_argument(*args, **kwargs)


def add_filepath_argument(parser, purpose=None):
    """Include the argument which is a path to a dotfile.

    :param purpose: Description of what will be done to the dotfile.
                    This is specific to particular command.
    """
    parser.add_argument(
        'filepath',
        metavar="FILE",
        help="Dotfile %s. The leading dot can be omitted." % (
            "to " + purpose if purpose else "path")
    )


def add_remote_url_argument(parser, required=False, desc=None):
    """Include the argument which asks for URL to remote dotfiles repository.

    :param required: Whether the argument must be supplied.
                     If ``False`` and it's omitted, default value of ``None``
                     will be used.
    :param desc: Description of the URL argument. This is somewhat specific
                 to the particular command.
    """
    desc = desc or "remote dotfiles repository"

    kwargs = dict(
        metavar="REMOTE_URL",
        help="Specify URL to %s." % desc,
    )
    if not required:
        kwargs.update(nargs='?', default=None)

    parser.add_argument('remote_url', **kwargs)


def add_home_dir_argument(parser):
    """Include the argument that allows to override what is considered
    a home directory (the one where dotfiles are normally stored).
    """
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


# Utility functions

def dotfile_repo(repo_dir):
    """argparse argument type for converting paths to moredots repositories
into :class:`DotfileRepo` objects automatically.
"""
    try:
        return DotfileRepo(repo_dir)
    except git.InvalidGitRepositoryError:
        msg = "fatal: %s is not a moredots repository" % repo_dir
        raise argparse.ArgumentError(msg)
