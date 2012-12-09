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

    repo.index.commit("[moredots] Initial setup")


# Utility functions

def create_argument_parser():
    """Creates argparse command-line parser."""
    parser = argparse.ArgumentParser(
        prog="mdots",
        description="Dotfiles manager based on Git",
        usage="mdots COMMAND [OPTIONS]",
    )
    subparsers = parser.add_subparsers(dest='command')

    init_parser = subparsers.add_parser('init')
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

    # TODO: add subparsers for add, rm, install and sync

    return parser
