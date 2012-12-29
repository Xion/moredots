#!/usr/e/v python
"""
Main module, containing program's entry point.
"""
from contextlib import contextmanager

from moredots import exc
from moredots.cmdline import create_argument_parser
from moredots.repo import DotfileRepo


def main():
    """Entry point."""
    parser = create_argument_parser()
    args = vars(parser.parse_args())

    # dispatch execution depending on what command was issued
    command = args.pop('command')
    command_handler = globals()['handle_%s' % command]
    with error_handler(command):
        return command_handler(**args)


# Handlers for different commands

def handle_init(repo_dir, home_dir):
    """Initialize dotfiles repository."""
    DotfileRepo.init(repo_dir, home_dir)


def handle_add(repo, filepath, hardlink):
    """Adds a dotfile to dotfiles repository."""
    repo.add(filepath, hardlink)


def handle_rm(repo, filepath):
    """Remove dotfile from dotfiles repository and return it
    to home directory intact.
    """
    repo.remove(filepath)


def handle_sync(repo, remote_url):
    """Synchronize dotfile repository with a remote one."""
    repo.sync(remote_url)


def handle_install(remote_url, repo_dir, home_dir):
    """Installs remote dotfiles repository on this machine."""
    DotfileRepo.install(remote_url, repo_dir, home_dir)


# Error handling

@contextmanager
def error_handler(command):
    """Context manager for top-level handling of errors that come
    from executing application commands.
    """
    # TODO: use logging module (after setting up neat log format)
    # instead of just printing stuff to stdout
    try:
        yield
    except exc.RepositoryExistsError, e:
        print "fatal: a repository already exists in " + e.repo_dir
    except exc.InvalidHomeDirError, e:
        print "fatal: cannot use %s as home directory" % e.home_dir
    except exc.DuplicateDotfileError, e:
        print "fatal: file %s already exists in the repository" % e.path
    except exc.DotfileNotFoundError, e:
        print "fatal: file %s does not exist in the repository" % e.path
    except exc.NoRemoteError:
        print "fatal: no remote to sync the repository with"


if __name__ == '__main__':
    main()
