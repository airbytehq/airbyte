/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.AirbyteDestinationRunner

object MSSQLDestination {
    @JvmStatic
    fun main(args: Array<String>) {
        // Must stay the first statement: it has to run before anything initializes TLS.
        TlsCompatibility.install()
        AirbyteDestinationRunner.run(*args)
    }
}
