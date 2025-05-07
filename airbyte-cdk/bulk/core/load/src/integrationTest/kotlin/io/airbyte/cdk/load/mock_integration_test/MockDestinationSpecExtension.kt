/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
class MockDestinationSpecExtension : DestinationSpecificationExtension {
    override val supportedSyncModes: List<DestinationSyncMode> =
        listOf(
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
            DestinationSyncMode.OVERWRITE,
        )
    override val supportsIncremental = true
}
