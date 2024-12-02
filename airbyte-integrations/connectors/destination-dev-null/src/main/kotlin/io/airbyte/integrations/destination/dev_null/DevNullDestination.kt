/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.AirbyteDestinationRunner

class DevNullDestination {
    companion object {
        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteDestinationRunner.run(*args)
        }
    }
}
