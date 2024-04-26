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
    CHECK_BASE_IMAGE = "check_base_image"
    CHECK_PYTHON_REGISTRY_PUBLISH_CONFIGURATION = "check_python_registry_publish_configuration"
    INTEGRATION = "integration"
    AIRBYTE_LIB_VALIDATION = "airbyte_lib_validation"
    METADATA_VALIDATION = "metadata_validation"
    QA_CHECKS = "qa_checks"
    UNIT = "unit"
    VERSION_FOLLOW_CHECK = "version_follow_check"
    VERSION_INC_CHECK = "version_inc_check"
    TEST_ORCHESTRATOR = "test_orchestrator"
    DEPLOY_ORCHESTRATOR = "deploy_orchestrator"
    UPDATE_README = "update_readme"
    ADD_CHANGELOG_ENTRY = "add_changelog_entry"
    BUMP_METADATA_VERSION = "bump_metadata_version"
    REGRESSION_TEST = "regression_test"
    CHECK_MIGRATION_CANDIDATE = "check_migration_candidate"
    POETRY_INIT = "poetry_init"
    DELETE_SETUP_PY = "delete_setup_py"
    CONNECTOR_REGRESSION_TESTS = "connector_regression_tests"

    def __str__(self) -> str:
        return self.value
