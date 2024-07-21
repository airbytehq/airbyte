import logging
import unittest

import foundry
from mockito import when, mock, unstub

from destination_palantir_foundry.config import validation
from destination_palantir_foundry.foundry_api import compass
from destination_palantir_foundry.foundry_api import foundry_auth
from destination_palantir_foundry.foundry_api import service_factory
from unit_tests.fixtures import FOUNDRY_CONFIG, FOUNDRY_HOST
from unit_tests.utils import stub_logger


class TestGetConfigErrors(unittest.TestCase):

    def setUp(self):
        self.logger = mock(logging.Logger)
        stub_logger(self.logger)

        self.auth = mock(
            spec=foundry.ConfidentialClientAuth)
        self.auth_factory = mock(
            spec=foundry_auth.ConfidentialClientAuthFactory, strict=True)

        self.compass = mock(compass.Compass)
        self.service_factory = mock(service_factory.FoundryServiceFactory)

        when(validation).FoundryServiceFactory(
            FOUNDRY_HOST, self.auth).thenReturn(self.service_factory)
        when(self.service_factory).compass().thenReturn(self.compass)

        self.config_validator = validation.ConfigValidator(
            self.logger,
            self.auth_factory
        )

    def tearDown(self):
        unstub()

    def test_getConfigErrors_invalidAuth_returnsError(self):
        when(self.auth_factory).create(FOUNDRY_CONFIG,
                                       validation.CONFIG_VALIDATION_SCOPES).thenReturn(self.auth)
        when(self.auth).sign_in_as_service_user().thenRaise(
            Exception("Authentication failed"))

        result = self.config_validator.get_config_errors(FOUNDRY_CONFIG)
        self.assertEqual(
            result, validation.FAILED_TO_AUTHENTICATE)

    def test_getConfigErrors_invalidProjectRid_returnsError(self):
        when(self.auth_factory).create(FOUNDRY_CONFIG,
                                       validation.CONFIG_VALIDATION_SCOPES).thenReturn(self.auth)
        when(self.auth).sign_in_as_service_user().thenReturn(None)

        when(self.compass).get_resource(FOUNDRY_CONFIG.destination_config.project_rid).thenRaise(
            Exception("Resource doesn't exist"))

        result = self.config_validator.get_config_errors(FOUNDRY_CONFIG)
        self.assertEqual(
            result, validation.PROJECT_DOESNT_EXIST)

    def test_getConfigErrors_allValid_returnsNone(self):
        when(self.auth_factory).create(FOUNDRY_CONFIG,
                                       validation.CONFIG_VALIDATION_SCOPES).thenReturn(self.auth)
        when(self.auth).sign_in_as_service_user().thenReturn(None)

        when(self.compass).get_resource(
            FOUNDRY_CONFIG.destination_config.project_rid).thenReturn(None)

        result = self.config_validator.get_config_errors(FOUNDRY_CONFIG)
        self.assertEqual(result, None)
