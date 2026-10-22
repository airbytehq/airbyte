/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake_g2

import io.airbyte.cdk.AirbyteDestinationRunner

object GcsDataLakeDestination {
    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteDestinationRunner.run(*args)
    }
}
