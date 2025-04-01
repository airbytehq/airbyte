/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.AirbyteDestinationRunner

object MSSQLDestination {
    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteDestinationRunner.run(*args)
    }
}
