# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

import docs


def test_docs_checked_in():
    """
    Docs need to be generated via `poetry run generate-docs` and checked in to the repo.

    This test runs the docs generation and compares the output with the checked in docs.
    It will fail if there are any differences.
    """

    docs.run()

    # compare the generated docs with the checked in docs
    diff = os.system("git diff --exit-code docs/generated")

    # if there is a diff, fail the test
    assert diff == 0, "Docs are out of date. Please run `poetry run generate-docs` and commit the changes."
