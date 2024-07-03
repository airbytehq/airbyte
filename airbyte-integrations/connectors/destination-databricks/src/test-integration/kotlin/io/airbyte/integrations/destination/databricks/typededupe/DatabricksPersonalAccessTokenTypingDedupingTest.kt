/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.typededupe

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout

class DatabricksPersonalAccessTokenTypingDedupingTest :
    AbstractDatabricksTypingDedupingTest(jdbcDatabase, connectorConfig) {
    companion object {
        private lateinit var jdbcDatabase: JdbcDatabase
        private lateinit var connectorConfig: DatabricksConnectorConfig

        @JvmStatic
        @BeforeAll
        @Timeout(value = 10, unit = TimeUnit.MINUTES)
        fun setupDatabase() {
            val (jdbcDatabase, connectorConfig) = setupDatabase("secrets/pat_config.json")
            this.jdbcDatabase = jdbcDatabase
            this.connectorConfig = connectorConfig
        }
    }
}
