# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from pathlib import Path

import git
import pytest
from asyncclick.testing import CliRunner

from connectors_qa.cli import generate_documentation

DOCUMENTATION_FILE_PATH_IN_AIRBYTE_REPO = Path("docs/contributing-to-airbyte/resources/qa-checks.md")


@pytest.fixture
def airbyte_repo():
    return git.Repo(search_parent_directories=True)


@pytest.mark.asyncio
async def test_generated_qa_checks_documentation_is_up_to_date(airbyte_repo, tmp_path):
    # Arrange
    current_doc = (airbyte_repo.working_dir / DOCUMENTATION_FILE_PATH_IN_AIRBYTE_REPO).read_text()
    newly_generated_doc_path = tmp_path / "qa-checks.md"

    # Act
    await CliRunner().invoke(generate_documentation, [str(tmp_path / "qa-checks.md")], catch_exceptions=False)

    # Assert
    suggested_command = f"connectors-qa generate-documentation {DOCUMENTATION_FILE_PATH_IN_AIRBYTE_REPO}"
    assert (
        newly_generated_doc_path.read_text() == current_doc
    ), f"The generated documentation is not up to date. Please run `{suggested_command}` and commit the changes."
