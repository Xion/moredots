"""
moredots -- root file
:author: Karol Kuczmarski "Xion"
"""
# TODO: it's a horrible mess -- divide it into modules, refactor & add tests

import os

import git

from moredots.cmdline import create_argument_parser


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
        print >>f, os.path.abspath(home_dir)

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


def handle_rm(repo, filepath):
    """Remove dotfile from dotfiles repository and return it
    to home directory intact.
    """
    with open(os.path.join(repo.working_dir, '.mdots', 'home')) as f:
        home_dir = f.read().strip()

     # TODO: add support for files inside dotdirectories, e.g. ~/.config
    _, filename = os.path.split(filepath)
    if filename.startswith('.'):
        filename = filename[1:]
    else:
        # TODO: this is brittle, use os.path functions instead
        filepath = filepath.replace(filename, '.%s' % filename)

    filepath = os.path.join(home_dir, filepath)
    dotfile_in_repo = os.path.join(repo.working_dir, filename)

    # TODO: for hardlinks, we can simply remove the in-repo file
    # instead of removing the home-dir file and doing the rename
    os.unlink(filepath)
    os.rename(dotfile_in_repo, filepath)

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

    # (sym)link dotfiles from the repo to home directory
    # TODO: this is duplicated from handle_install, extract to separate function
    with open(os.path.join(repo.working_dir, '.mdots', 'home')) as f:
        home_dir = f.read().strip()
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
            print repo_path, '->', home_path

            if os.path.exists(home_path):
                os.unlink(home_path)
            os.symlink(repo_path, home_path)  # TODO: support hardlinks


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
        print >>f, os.path.abspath(home_dir)

    # (sym)link dotfiles from the repo to home directory
    for directory, subdirs, filenames in os.walk(repo_dir):
        for skipdir in ['.git', '.mdots']:
            if skipdir in subdirs:
                subdirs.remove(skipdir)
        for filename in filenames:
            if filename.startswith('.'):  # these are repo's internal dotfiles,
                continue                  # such as .gitignore

            # TODO: add support for files inside dot-directories
            repo_path = os.path.join(directory, filename)
            home_path = os.path.join(home_dir, '.' + filename)
            print repo_path, '->', home_path

            if os.path.exists(home_path):
                os.unlink(home_path)
            os.symlink(repo_path, home_path)  # TODO: support hardlinks

