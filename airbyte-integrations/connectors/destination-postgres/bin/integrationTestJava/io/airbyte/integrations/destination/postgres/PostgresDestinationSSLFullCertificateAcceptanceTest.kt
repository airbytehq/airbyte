/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import org.junit.jupiter.api.Disabled

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
class PostgresDestinationSSLFullCertificateAcceptanceTest :
    AbstractPostgresDestinationAcceptanceTest() {
    private var testDb: PostgresTestDatabase? = null

    override val imageName: String
        get() = "airbyte/destination-postgres:dev"

    override fun getConfig(): JsonNode {
        return testDb!!
            .configBuilder()
            .with("schema", "public")
            .withDatabase()
            .withResolvedHostAndPort()
            .withCredentials()
            .withSsl(
                ImmutableMap.builder<Any?, Any?>()
                    .put(
                        "mode",
                        "verify-ca"
                    ) // verify-full will not work since the spawned container is only allowed for
                    // 127.0.0.1/32 CIDRs
                    .put("ca_certificate", testDb!!.certificates.caCertificate)
                    .build()
            )
            .build()
    }

    override fun getTestDb(): PostgresTestDatabase {
        return testDb!!
    }

    @Throws(Exception::class)
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        testDb =
            PostgresTestDatabase.`in`(
                PostgresTestDatabase.BaseImage.POSTGRES_12,
                PostgresTestDatabase.ContainerModifier.CERT
            )
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv) {
        testDb!!.close()
    }

    @Disabled("Custom DBT does not have root certificate created in the Postgres container.")
    @Throws(Exception::class)
    override fun testCustomDbtTransformations() {
        super.testCustomDbtTransformations()
    }
}
