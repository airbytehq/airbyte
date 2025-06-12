#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module declaring context related classes."""

from copy import deepcopy
from logging import Logger
from typing import Any, Dict, List, Optional

from pydash import find  # type: ignore

from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.helpers.execution.run_steps import RunStepOptions
from pipelines.models.secrets import Secret, SecretNotFoundError, SecretStore

# These test suite names are declared in metadata.yaml files
TEST_SUITE_NAME_TO_STEP_ID = {
    "unitTests": CONNECTOR_TEST_STEP_ID.UNIT,
    "integrationTests": CONNECTOR_TEST_STEP_ID.INTEGRATION,
    "acceptanceTests": CONNECTOR_TEST_STEP_ID.ACCEPTANCE,
    "liveTests": CONNECTOR_TEST_STEP_ID.CONNECTOR_LIVE_TESTS,
}


class ConnectorTestContext(ConnectorContext):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.run_step_options = self._skip_metadata_disabled_test_suites(self.run_step_options)
        self.step_id_to_secrets_mapping = self._get_step_id_to_secret_mapping()

    @staticmethod
    def _handle_missing_secret_store(
        secret_info: Dict[str, str | Dict[str, str]], raise_on_missing: bool, logger: Optional[Logger] = None
    ) -> None:
        assert isinstance(secret_info["secretStore"], dict), "The secretStore field must be a dict"
        message = f"Secret {secret_info['name']} can't be retrieved as {secret_info['secretStore']['alias']} is not available"
        if raise_on_missing:
            raise SecretNotFoundError(message)
        if logger is not None:
            logger.warn(message)

    @staticmethod
    def _process_secret(
        secret_info: Dict[str, str | Dict[str, str]],
        secret_stores: Dict[str, SecretStore],
        raise_on_missing: bool,
        logger: Optional[Logger] = None,
    ) -> Optional[Secret]:
        assert isinstance(secret_info["secretStore"], dict), "The secretStore field must be a dict"
        secret_store_alias = secret_info["secretStore"]["alias"]
        if secret_store_alias not in secret_stores:
            ConnectorTestContext._handle_missing_secret_store(secret_info, raise_on_missing, logger)
            return None
        else:
            # All these asserts and casting are there to make MyPy happy
            # The dict structure being nested MyPy can't figure if the values are str or dict
            assert isinstance(secret_info["name"], str), "The secret name field must be a string"
            if file_name := secret_info.get("fileName"):
                assert isinstance(secret_info["fileName"], str), "The secret fileName must be a string"
                file_name = str(secret_info["fileName"])
            else:
                file_name = None
            return Secret(secret_info["name"], secret_stores[secret_store_alias], file_name=file_name)

    @staticmethod
    def get_secrets_from_connector_test_suites_option(
        connector_test_suites_options: List[Dict[str, str | Dict[str, List[Dict[str, str | Dict[str, str]]]]]],
        suite_name: str,
        secret_stores: Dict[str, SecretStore],
        raise_on_missing_secret_store: bool = True,
        logger: Logger | None = None,
    ) -> List[Secret]:
        """Get secrets declared in metadata connectorTestSuitesOptions for a test suite name.
        It will use the secret store alias declared in connectorTestSuitesOptions.
        If the secret store is not available a warning or and error could be raised according to the raise_on_missing_secret_store parameter value.
        We usually want to raise an error when running in CI context and log a warning when running locally, as locally we can fallback on local secrets.

        Args:
            connector_test_suites_options (List[Dict[str, str  |  Dict]]): The connector under test test suite options
            suite_name (str): The test suite name
            secret_stores (Dict[str, SecretStore]): The available secrets stores
            raise_on_missing_secret_store (bool, optional): Raise an error if the secret store declared in the connectorTestSuitesOptions is not available. Defaults to True.
            logger (Logger | None, optional): Logger to log a warning if the secret store declared in the connectorTestSuitesOptions is not available. Defaults to None.

        Raises:
            SecretNotFoundError: Raised  if the secret store declared in the connectorTestSuitesOptions is not available and raise_on_missing_secret_store is truthy.

        Returns:
            List[Secret]: List of secrets declared in the connectorTestSuitesOptions for a test suite name.
        """
        secrets: List[Secret] = []
        enabled_test_suite = find(connector_test_suites_options, lambda x: x["suite"] == suite_name)

        if enabled_test_suite and "testSecrets" in enabled_test_suite:
            for secret_info in enabled_test_suite["testSecrets"]:
                if secret := ConnectorTestContext._process_secret(secret_info, secret_stores, raise_on_missing_secret_store, logger):
                    secrets.append(secret)
        return secrets

    def get_connector_secrets_for_test_suite(
        self, test_suite_name: str, connector_test_suites_options: List, local_secrets: List[Secret]
    ) -> List[Secret]:
        """Get secrets to use for a test suite.
        Always merge secrets declared in metadata's connectorTestSuiteOptions with secrets declared locally.

        Args:
            test_suite_name (str): Name of the test suite to get secrets for
            context (ConnectorTestContext): The current connector context
            connector_test_suites_options (Dict): The current connector test suite options (from metadata)
            local_secrets (List[Secret]): The local connector secrets.

        Returns:
            List[Secret]: Secrets to use to run the passed test suite name.
        """
        return (
            self.get_secrets_from_connector_test_suites_option(
                connector_test_suites_options,
                test_suite_name,
                self.secret_stores,
                raise_on_missing_secret_store=self.is_ci,
                logger=self.logger,
            )
            + local_secrets
        )

    def _get_step_id_to_secret_mapping(self) -> Dict[CONNECTOR_TEST_STEP_ID, List[Secret]]:
        step_id_to_secrets: Dict[CONNECTOR_TEST_STEP_ID, List[Secret]] = {
            CONNECTOR_TEST_STEP_ID.UNIT: [],
            CONNECTOR_TEST_STEP_ID.INTEGRATION: [],
            CONNECTOR_TEST_STEP_ID.ACCEPTANCE: [],
        }
        local_secrets = self.local_secret_store.get_all_secrets() if self.local_secret_store else []
        connector_test_suites_options = self.metadata.get("connectorTestSuitesOptions", [])

        keep_steps = set(self.run_step_options.keep_steps or [])
        skip_steps = set(self.run_step_options.skip_steps or [])

        for test_suite_name, step_id in TEST_SUITE_NAME_TO_STEP_ID.items():
            if step_id in keep_steps or (not keep_steps and step_id not in skip_steps):
                step_id_to_secrets[step_id] = self.get_connector_secrets_for_test_suite(
                    test_suite_name, connector_test_suites_options, local_secrets
                )
        return step_id_to_secrets

    def get_secrets_for_step_id(self, step_id: CONNECTOR_TEST_STEP_ID) -> List[Secret]:
        return self.step_id_to_secrets_mapping.get(step_id, [])

    def _get_step_id_to_skip_according_to_metadata(self) -> List[CONNECTOR_TEST_STEP_ID]:
        """The connector metadata have a connectorTestSuitesOptions field.
        It allows connector developers to declare the test suites that are enabled for a connector.
        This function retrieved enabled test suites according to this field value and returns the test suites steps that are skipped (because they're not declared in this field.)
        The skippable test suites steps are declared in TEST_SUITE_NAME_TO_STEP_ID.

        Returns:
            List[CONNECTOR_TEST_STEP_ID]: List of step ids that should be skipped according to connector metadata.
        """
        enabled_test_suites = [option["suite"] for option in self.metadata.get("connectorTestSuitesOptions", [])]
        return [step_id for test_suite_name, step_id in TEST_SUITE_NAME_TO_STEP_ID.items() if test_suite_name not in enabled_test_suites]

    def _skip_metadata_disabled_test_suites(self, run_step_options: RunStepOptions) -> RunStepOptions:
        """Updated the original run_step_options to skip the disabled test suites according to connector metadata.

        Args:
            run_step_options (RunStepOptions): Original run step options.

        Returns:
            RunStepOptions: Updated run step options.
        """
        run_step_options = deepcopy(run_step_options)
        # If any `skip_steps` are present, we will run everything except the skipped steps, instead of just `keep_steps`.
        if not run_step_options.keep_steps:
            run_step_options.skip_steps += self._get_step_id_to_skip_according_to_metadata()
        return run_step_options
