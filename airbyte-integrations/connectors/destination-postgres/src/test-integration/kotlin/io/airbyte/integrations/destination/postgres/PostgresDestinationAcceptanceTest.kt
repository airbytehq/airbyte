/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.fasterxml.jackson.databind.JsonNode
import org.junit.jupiter.api.Disabled

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
class PostgresDestinationAcceptanceTest : AbstractPostgresDestinationAcceptanceTest() {
    private var testDb: PostgresTestDatabase? = null

    override fun getConfig(): JsonNode {
        return testDb!!
            .configBuilder()
            .with("schema", "public")
            .withDatabase()
            .withResolvedHostAndPort()
            .withCredentials()
            .withoutSsl()
            .build()
    }

    override fun getTestDb(): PostgresTestDatabase {
        return testDb!!
    }

    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        testDb = PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_13)
    }

    override fun tearDown(testEnv: TestDestinationEnv) {
        testDb!!.close()
    }
}
