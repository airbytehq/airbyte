# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import os
from pathlib import Path

import git


def _validate_airbyte_repo(repo: git.Repo) -> bool:
    """Check if any of the remotes are the airbyte repo."""
    expected_repo_name = "airbytehq/airbyte"
    for remote in repo.remotes:
        if expected_repo_name in remote.url:
            return True

    warning_message = f"""
    ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️

    It looks like you are not running this command from the airbyte repo ({expected_repo_name}).

    If this command is run from outside the airbyte repo, it will not work properly.

    Please run this command your local airbyte project.

    ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
    """

    logging.warning(warning_message)

    return False


def get_airbyte_repo() -> git.Repo:
    """Get the airbyte repo."""
    repo = git.Repo(search_parent_directories=True)
    _validate_airbyte_repo(repo)
    return repo


def get_airbyte_repo_path_with_fallback() -> Path:
    """Get the path to the airbyte repo."""
    try:
        repo_path = get_airbyte_repo().working_tree_dir
        if repo_path is not None:
            return Path(str(get_airbyte_repo().working_tree_dir))
    except git.exc.InvalidGitRepositoryError:
        pass
    logging.warning("Could not find the airbyte repo, falling back to the current working directory.")
    path = Path.cwd()
    logging.warning(f"Using {path} as the airbyte repo path.")
    return path


def set_working_directory_to_root() -> None:
    """Set the working directory to the root of the airbyte repo."""
    working_dir = get_airbyte_repo_path_with_fallback()
    logging.info(f"Setting working directory to {working_dir}")
    os.chdir(working_dir)
