"""
Unit tests for command line parser.
"""
from moredots.cmdline import create_argument_parser

import pytest


# Tests

def test_init_without_args(argparser):
    argparser.parse_args(['init'])


def test_init_with_repo_arg(argparser, tmpdir):
    repo_dir = str(tmpdir)
    args = argparser.parse_args(['init', repo_dir])

    assert args.repo_dir == repo_dir


# Fixtures / resources

@pytest.fixture
def argparser():
    """Provide argparse ArgumentParser for tests."""
    return create_argument_parser()
