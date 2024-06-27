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
import org.junit.jupiter.api.Test

open class PostgresTypingDedupingTest : AbstractPostgresTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return testContainer!!
            .configBuilder()
            .with("schema", "public")
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

    @Test
    override fun incrementalDedup() {
        super.incrementalDedup();
    }

    @Test
    override fun truncateRefresh() {
        super.truncateRefresh();
    }

    @Test
    override fun incrementalAppend() {
        super.incrementalAppend();
    }

    @Test
    override fun incrementalDedupChangeCursor() {
        super.incrementalDedupChangeCursor();
    }

    @Test
    override fun largeDedupSync() {
        super.largeDedupSync();
    }

    @Test
    override fun testMixedCasedSchema() {
        super.testMixedCasedSchema();
    }

    @Test
    override fun mergeRefresh() {
        super.mergeRefresh();
    }

    @Test
    override fun testRawTableMetaMigration_append() {
        super.testRawTableMetaMigration_append();
    }

    @Test
    override fun testRawTableMetaMigration_incrementalDedupe() {
        super.testRawTableMetaMigration_incrementalDedupe();
    }

    @Test
    override fun testMixedCaseRawTableV1V2Migration() {
        super.testMixedCaseRawTableV1V2Migration();
    }

    @Test
    override fun identicalNameSimultaneousSync() {
        super.identicalNameSimultaneousSync();
    }
}
