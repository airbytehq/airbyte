/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.base.ssh.SshTunnel
import io.airbyte.configoss.StandardCheckConnectionOutput
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
class PostgresDestinationStrictEncryptAcceptanceTest : AbstractPostgresDestinationAcceptanceTest() {
    private var testDb: PostgresTestDatabase? = null

    override val imageName: String
        get() = "airbyte/destination-postgres-strict-encrypt:dev"

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

    override fun tearDown(testEnv: TestDestinationEnv) {
        testDb!!.close()
    }

    @Test
    @Throws(Exception::class)
    fun testStrictSSLUnsecuredNoTunnel() {
        val config: JsonNode =
            testDb!!
                .configBuilder()
                .with("schema", "public")
                .withDatabase()
                .withResolvedHostAndPort()
                .withCredentials()
                .with(
                    "tunnel_method",
                    ImmutableMap.builder<Any, Any>()
                        .put("tunnel_method", SshTunnel.TunnelMethod.NO_TUNNEL.toString())
                        .build()
                )
                .with("ssl_mode", ImmutableMap.builder<Any, Any>().put("mode", "prefer").build())
                .build()
        val actual = runCheck(config)
        Assertions.assertEquals(StandardCheckConnectionOutput.Status.FAILED, actual.status)
        Assertions.assertTrue(actual.message.contains("Unsecured connection not allowed"))
    }

    @Test
    @Throws(Exception::class)
    fun testStrictSSLSecuredNoTunnel() {
        val config: JsonNode =
            testDb!!
                .configBuilder()
                .with("schema", "public")
                .withDatabase()
                .withResolvedHostAndPort()
                .withCredentials()
                .with(
                    "tunnel_method",
                    ImmutableMap.builder<Any, Any>()
                        .put("tunnel_method", SshTunnel.TunnelMethod.NO_TUNNEL.toString())
                        .build()
                )
                .with("ssl_mode", ImmutableMap.builder<Any, Any>().put("mode", "require").build())
                .build()
        val actual = runCheck(config)
        Assertions.assertEquals(StandardCheckConnectionOutput.Status.SUCCEEDED, actual.status)
    }

    override fun normalizationFromDefinition(): Boolean {
        return true
    }

    override fun dbtFromDefinition(): Boolean {
        return true
    }

    override val destinationDefinitionKey: String
        get() = "airbyte/destination-postgres"

    override fun supportsInDestinationNormalization(): Boolean {
        return true
    }

    @Disabled("Custom DBT does not have root certificate created in the Postgres container.")
    @Throws(Exception::class)
    override fun testCustomDbtTransformations() {
        super.testCustomDbtTransformations()
    }

    companion object {
        protected const val PASSWORD: String = "Passw0rd"
    }
}
