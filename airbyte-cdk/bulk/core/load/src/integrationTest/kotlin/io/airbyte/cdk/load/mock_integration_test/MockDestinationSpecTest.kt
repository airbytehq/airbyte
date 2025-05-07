/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.spec.SpecTest
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT

class MockDestinationSpecTest :
    SpecTest(additionalMicronautEnvs = listOf(MOCK_TEST_MICRONAUT_ENVIRONMENT))
