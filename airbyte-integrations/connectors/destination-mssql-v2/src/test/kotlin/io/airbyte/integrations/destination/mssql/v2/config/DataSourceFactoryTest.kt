/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import org.junit.jupiter.api.Test

internal class DataSourceFactoryTest {

    @Test
    fun test() {
        val factory = DataSourceFactory()
        val dataSource = factory.dataSource()

        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute("SELECT * FROM Inventory")
            }
        }
    }
}
