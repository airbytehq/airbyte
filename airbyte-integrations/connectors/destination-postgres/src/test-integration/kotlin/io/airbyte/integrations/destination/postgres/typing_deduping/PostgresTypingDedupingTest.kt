/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.integrations.destination.postgres.PostgresDestination
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase
import javax.sql.DataSource
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll

open class PostgresTypingDedupingTest : AbstractPostgresTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return testContainer!!
            .configBuilder()
            .with("schema", "public")
            .with(PostgresDestination.DROP_CASCADE_OPTION, true)
            .withDatabase()
            .withResolvedHostAndPort()
            .withCredentials()
            .withoutSsl()
            .build()
    }

    override fun getDataSource(config: JsonNode?): DataSource? {
        // Intentionally ignore the config and rebuild it.
        // The config param has the resolved (i.e. in-docker) host/port.
        // We need the unresolved host/port since the test wrapper code is running from the docker
        // host
        // rather than in a container.
        return PostgresDestination()
            .getDataSource(
                testContainer!!
                    .configBuilder()
                    .with("schema", "public")
                    .withDatabase()
                    .withHostAndPort()
                    .withCredentials()
                    .withoutSsl()
                    .build()
            )
    }

    override val imageName: String
        get() = "airbyte/destination-postgres:dev"

    companion object {
        protected var testContainer: PostgresTestDatabase? = null

        @JvmStatic
        @BeforeAll
        fun setupPostgres() {
            testContainer = PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_13)
        }

        @JvmStatic
        @AfterAll
        fun teardownPostgres() {
            testContainer!!.close()
        }
    }
}
