/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class SnowflakeDestinationHandlerTest {

    private val database = mockk<JdbcDatabase>()
    private val destinationHandler =
        SnowflakeDestinationHandler("mock-database-name", database, "mock-schema")

    @Test fun execute() {}

    @Test fun createNamespaces() {}
}
