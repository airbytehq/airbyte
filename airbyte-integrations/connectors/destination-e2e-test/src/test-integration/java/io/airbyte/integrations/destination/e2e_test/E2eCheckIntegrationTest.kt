/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test

import io.airbyte.cdk.test.check.CheckIntegrationTest

class E2eCheckIntegrationTest :
    CheckIntegrationTest<E2EDestinationConfigurationJsonObject>(
        E2EDestinationConfigurationJsonObject::class.java,
        successConfigFilenames = listOf(E2eTestUtils.LOGGING_CONFIG_PATH),
        failConfigFilenamesAndFailureReasons = mapOf(),
    )
