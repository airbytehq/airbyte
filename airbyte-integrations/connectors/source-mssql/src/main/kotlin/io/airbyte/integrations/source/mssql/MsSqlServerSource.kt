/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.AirbyteSourceRunner

object MsSqlServerSource {
    @JvmStatic
    fun main(args: Array<String>) {
        // Must stay the first statement: it has to run before anything initializes TLS.
        TlsCompatibility.install()
        AirbyteSourceRunner.run(*args)
    }
}
