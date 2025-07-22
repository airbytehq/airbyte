/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload.check

import io.airbyte.cdk.load.check.CheckCleaner
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.skeleton_directload.spec.SkeletonDirectLoadConfiguration

class SkeletonDirectLoadCheckCleaner : CheckCleaner<SkeletonDirectLoadConfiguration> {
    override fun cleanup(config: SkeletonDirectLoadConfiguration, stream: DestinationStream) {
        // Here we cleanup whatever has been created during the DirectLoad operation
    }
}
