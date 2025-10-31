/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.integrations.destination.postgres.PostgresDestination
import javax.sql.DataSource
import kotlin.longArrayOf
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

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

    //syncs used to fail when doing this, not anymore
    @Disabled @Test override fun interruptedTruncateWithPriorData() {}

    // fields that are not in the schema are now dropped.
    @Disabled @ParameterizedTest @ValueSource(longs = [0L, 42L]) override fun testIncrementalSyncDropOneColumn(inputGenerationId: Long) {}

    //migrations not supported on most recent version
    @Disabled @Test override fun testMixedCaseRawTableV1V2Migration() {}
    @Disabled @Test override fun testAirbyteMetaAndGenerationIdMigration() {}
    @Disabled @Test override fun testRawTableMetaMigration_append() {}
    @Disabled @Test override fun testRawTableMetaMigration_incrementalDedupe() {}
    @Disabled @Test override fun testAirbyteMetaAndGenerationIdMigrationForOverwrite() {}

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
