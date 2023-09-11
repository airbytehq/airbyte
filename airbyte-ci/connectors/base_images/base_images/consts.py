#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

import dagger
import git

AIRBYTE_GITHUB_REPO_URL = "https://github.com/airbytehq/airbyte"
GIT_REPO = git.Repo(search_parent_directories=True)
AIRBYTE_ROOT_DIR = GIT_REPO.working_tree_dir
MAIN_BRANCH_NAME = "master"
PROJECT_DIR = Path(__file__).parent.parent
SUPPORTED_PLATFORMS = (dagger.Platform("linux/amd64"), dagger.Platform("linux/arm64"))
