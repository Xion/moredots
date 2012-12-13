"""
moredots -- root file
:author: Karol Kuczmarski "Xion"
"""
# TODO: it's a horrible mess -- divide it into modules, refactor & add tests

import os

import git

from moredots.cmdline import create_argument_parser
from moredots.files import (install_dotfiles, set_home_dir,
                            move_dotfile_to_repo, remove_dotfile_from_repo)


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
    set_home_dir(repo, home_dir)

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

    # setting up remote branch tracking for subsequent `mdots sync`
    repo.head.ref.set_tracking_branch(origin.refs.master)

    install_dotfiles(repo)


def handle_install(remote_url, repo_dir, home_dir):
    """Installs remote dotfiles repository on this machine."""
    repo_gitdir = os.path.join(repo_dir, '.git')
    if git.repo.fun.is_git_dir(repo_gitdir):
        print "fatal: %s is already a Git repository" % repo_dir
        return

    # TODO: implement progress tracking for this operation
    repo = git.Repo.clone_from(remote_url, repo_dir)

    set_home_dir(repo, home_dir)
    install_dotfiles(repo)
