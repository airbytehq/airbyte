/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(env = [MOCK_TEST_MICRONAUT_ENVIRONMENT])
class MockDestinationSpecExtension : DestinationSpecificationExtension {
    override val supportedSyncModes: List<DestinationSyncMode> =
        listOf(
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
            DestinationSyncMode.OVERWRITE,
        )
    override val supportsIncremental = true
}
