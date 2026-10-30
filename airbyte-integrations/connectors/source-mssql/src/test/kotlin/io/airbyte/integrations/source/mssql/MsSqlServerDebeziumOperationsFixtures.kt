/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.mockk.mockk

/** [MsSqlServerDebeziumOperations] for tests of logic that never opens a connection. */
internal fun debeziumOperationsWithoutDatabase(): MsSqlServerDebeziumOperations {
    val spec =
        MsSqlServerSourceConfigurationSpecification().apply {
            host = "localhost"
            port = 1433
            database = "test"
            username = "sa"
            password = "Password123!"
            setIncrementalValue(Cdc())
        }
    return MsSqlServerDebeziumOperations(
        mockk<JdbcConnectionFactory>(relaxed = true),
        MsSqlServerSourceConfigurationFactory().make(spec),
    )
}
