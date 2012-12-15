"""
Shared utility code for tests.
"""
import git

import pytest


# Fixtures / resources

@pytest.fixture
def git_repo(tmpdir):
    """Provides a local Git repository, created in a temporary directory."""
    return git.Repo.init(str(tmpdir))
