/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.integrations.destination.postgres.PostgresDestination
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase
import javax.sql.DataSource
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

// TODO: This test is added to ensure coverage missed by disabling DATs. Redundant when DATs
// enabled.
class PostgresStrictEncryptTypingDedupingTest : AbstractPostgresTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return testContainer!!
            .configBuilder()
            .with("schema", "public")
            .withDatabase()
            .withResolvedHostAndPort()
            .withCredentials()
            .with(PostgresDestination.DROP_CASCADE_OPTION, true)
            .withSsl(
                ImmutableMap.builder<Any?, Any?>()
                    .put(
                        "mode",
                        "verify-ca"
                    ) // verify-full will not work since the spawned container is only allowed for
                    // 127.0.0.1/32 CIDRs
                    .put("ca_certificate", testContainer!!.certificates.caCertificate)
                    .build()
            )
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
        get() = "airbyte/destination-postgres-strict-encrypt:dev"

    @Test
    override fun testDropCascade() {
        super.testDropCascade()
    }

    @Test
    override fun interruptedTruncateWithPriorData() {
        super.interruptedTruncateWithPriorData()
    }

    companion object {
        protected var testContainer: PostgresTestDatabase? = null

        @JvmStatic
        @BeforeAll
        fun setupPostgres(): Unit {
            // Postgres-13 is alpine image and SSL conf is failing to load, intentionally using
            // 12:bullseye
            testContainer =
                PostgresTestDatabase.`in`(
                    PostgresTestDatabase.BaseImage.POSTGRES_12,
                    PostgresTestDatabase.ContainerModifier.CERT
                )
        }

        @JvmStatic
        @AfterAll
        fun teardownPostgres(): Unit {
            testContainer!!.close()
        }
    }
}
