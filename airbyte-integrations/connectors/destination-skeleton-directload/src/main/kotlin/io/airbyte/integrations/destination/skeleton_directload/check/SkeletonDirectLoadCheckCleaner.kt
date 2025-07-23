/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload.check

import io.airbyte.cdk.load.check.CheckCleaner
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.skeleton_directload.spec.SkeletonDirectLoadConfiguration

class SkeletonDirectLoadCheckCleaner : CheckCleaner<SkeletonDirectLoadConfiguration> {
    override fun cleanup(
        @Suppress("UNUSED_PARAMETER")
        config: SkeletonDirectLoadConfiguration,
        @Suppress("UNUSED_PARAMETER")
        stream: DestinationStream
    ) {
        // Here we clean up whatever has been created during the DirectLoad operation
    }
}
