# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from enum import Enum


class CONNECTOR_TEST_STEP_ID(str, Enum):
    """
    An enum for the different step ids of the connector test pipeline.
    """

    ACCEPTANCE = "acceptance"
    BUILD_NORMALIZATION = "build_normalization"
    BUILD_TAR = "build_tar"
    BUILD = "build"
    INTEGRATION = "integration"
    AIRBYTE_LIB_VALIDATION = "airbyte_lib_validation"
    QA_CHECKS = "qa_checks"
    UNIT = "unit"
    VERSION_INC_CHECK = "version_inc_check"
    TEST_ORCHESTRATOR = "test_orchestrator"
    DEPLOY_ORCHESTRATOR = "deploy_orchestrator"
    MIGRATE_POETRY_UPDATE_README = "migrate_to_poetry.update_readme"
    MIGRATE_POETRY_CHECK_MIGRATION_CANDIDATE = "migrate_to_poetry.check_migration_candidate"
    MIGRATE_POETRY_POETRY_INIT = "migrate_to_poetry.poetry_init"
    MIGRATE_POETRY_DELETE_SETUP_PY = "migrate_to_poetry.delete_setup_py"
    MIGRATE_POETRY_REGRESSION_TEST = "migrate_to_poetry.regression"
    CONNECTOR_REGRESSION_TESTS = "connector_regression_tests"
    REGRESSION_TEST = "common.regression_test"
    ADD_CHANGELOG_ENTRY = "bump_version.changelog"
    SET_CONNECTOR_VERSION = "bump_version.set"
    CHECK_UPDATE_CANDIDATE = "up_to_date.check"
    UPDATE_POETRY = "up_to_date.poetry"
    UPDATE_PULL_REQUEST = "up_to_date.pull"
    INLINE_CANDIDATE = "migration_to_inline_schemas.candidate"
    INLINE_MIGRATION = "migration_to_inline_schemas.migration"
    PULL_REQUEST_CREATE = "pull_request.create"
    PULL_REQUEST_UPDATE = "pull_request.update"

    def __str__(self) -> str:
        return self.value
