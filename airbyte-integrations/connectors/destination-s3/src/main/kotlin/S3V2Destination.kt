/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.AirbyteDestinationRunner

class S3V2Destination {
    companion object {
        val ENVIRONMENTS = arrayOf("s3")
        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteDestinationRunner.run(*args, additionalEnvironments = ENVIRONMENTS)
        }
    }
}
