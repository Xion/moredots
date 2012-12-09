"""
moredots -- root file
:author: Karol Kuczmarski "Xion"
"""
import os
import argparse


def main():
    """Entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()


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
             "on a single machine."
    )

    # TODO: add subparsers for add, rm, install and sync

    return parser
