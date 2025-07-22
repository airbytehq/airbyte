/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.skeleton_directload

import io.airbyte.cdk.AirbyteDestinationRunner

class SkeletonDirectLoadDestination {
    companion object {
        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteDestinationRunner.run(*args)
        }
    }
}
