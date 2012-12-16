"""
moredots -- root file
:author: Karol Kuczmarski "Xion"
"""
# TODO: it's a horrible mess -- divide it into modules, refactor & add tests

import os

import git

from moredots.cmdline import create_argument_parser
from moredots.files import move_dotfile_to_repo, remove_dotfile_from_repo
from moredots.repo import DotfileRepo


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

    DotfileRepo.init(repo_dir, home_dir)


def handle_add(repo, filepath, hardlink):
    """Adds a dotfile to dotfiles repository."""

    # TODO: add support for files inside dotdirectories, e.g. ~/.config
    _, filename = os.path.split(filepath)
    if filename.startswith('.'):
        filename = filename[1:]
    else:
        # TODO: this is brittle, use os.path functions instead
        filepath = filepath.replace(filename, '.%s' % filename)

    move_dotfile_to_repo(filepath, repo, hardlink)

    # commit changes
    repo.index.add([filename])
    repo.index.commit("[moredots] Add .%s" % filename)


def handle_rm(repo, filepath):
    """Remove dotfile from dotfiles repository and return it
    to home directory intact.
    """
     # TODO: add support for files inside dotdirectories, e.g. ~/.config
    _, filename = os.path.split(filepath)
    if filename.startswith('.'):
        filename = filename[1:]
    else:
        # TODO: this is brittle, use os.path functions instead
        filepath = filepath.replace(filename, '.%s' % filename)

    remove_dotfile_from_repo(filepath, repo)

    repo.index.remove([filename])
    repo.index.commit("[moredots] Remove .%s" % filename)


def handle_sync(repo, remote_url):
    DotfileRepo(repo).sync(remote_url)


def handle_install(remote_url, repo_dir, home_dir):
    """Installs remote dotfiles repository on this machine."""
    repo_gitdir = os.path.join(repo_dir, '.git')
    if git.repo.fun.is_git_dir(repo_gitdir):
        print "fatal: %s is already a Git repository" % repo_dir
        return

    DotfileRepo.install(remote_url, repo_dir, home_dir)
