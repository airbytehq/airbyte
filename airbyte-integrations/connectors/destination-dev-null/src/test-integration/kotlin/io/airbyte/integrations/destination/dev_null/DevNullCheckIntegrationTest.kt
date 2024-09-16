/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.test.check.CheckIntegrationTest

class DevNullCheckIntegrationTest :
    CheckIntegrationTest<DevNullSpecification>(
        DevNullSpecification::class.java,
        successConfigFilenames = listOf(DevNullTestUtils.LOGGING_CONFIG_PATH),
        failConfigFilenamesAndFailureReasons = mapOf(),
    )
