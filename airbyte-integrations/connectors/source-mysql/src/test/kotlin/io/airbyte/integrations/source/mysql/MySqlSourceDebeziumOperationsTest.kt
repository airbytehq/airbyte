/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
import io.airbyte.integrations.source.mysql.MySqlSourceDebeziumOperations.Companion.addDebeziumSslPropertiesFromJdbcProperties
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MySqlSourceDebeziumOperationsTest {

    /**
     * Regression test for airbytehq/oncall#12344 (and the earlier airbytehq/oncall#7859): when CDC
     * is configured together with `verify_ca` (or `verify_identity`) SSL and client certificates,
     * the Debezium binlog client must receive the corresponding `database.ssl.*` properties,
     * otherwise it silently falls back to `preferred` mode and ignores the configured trust/key
     * stores. The result is an authentication failure on the binlog connection while the JDBC
     * snapshot connection works fine.
     */
    @Test
    fun verifyCaWithClientCertProducesDebeziumSslProperties() {
        val truststorePath: Path = Files.createTempFile("source-mysql-truststore", ".p12")
        val keystorePath: Path = Files.createTempFile("source-mysql-keystore", ".p12")
        try {
            val jdbcProperties: Map<String, String> =
                mapOf(
                    MySqlSourceConfigurationFactory.SSL_MODE to "verify_ca",
                    MySqlSourceConfigurationFactory.TRUST_KEY_STORE_URL to
                        truststorePath.toUri().toString(),
                    MySqlSourceConfigurationFactory.TRUST_KEY_STORE_PASS to "trust-pass",
                    MySqlSourceConfigurationFactory.TRUST_KEY_STORE_TYPE to
                        MySqlSourceConfigurationFactory.KEY_STORE_TYPE_PKCS12,
                    MySqlSourceConfigurationFactory.CLIENT_KEY_STORE_URL to
                        keystorePath.toUri().toString(),
                    MySqlSourceConfigurationFactory.CLIENT_KEY_STORE_PASS to "client-pass",
                    MySqlSourceConfigurationFactory.CLIENT_KEY_STORE_TYPE to
                        MySqlSourceConfigurationFactory.KEY_STORE_TYPE_PKCS12,
                )

            val builder = DebeziumPropertiesBuilder().withDatabase(jdbcProperties)
            addDebeziumSslPropertiesFromJdbcProperties(builder, jdbcProperties)
            val props: Map<String, String> = builder.buildMap()

            // The binlog client uses these Debezium-specific SSL properties.
            Assertions.assertEquals("verify_ca", props["database.ssl.mode"])
            Assertions.assertEquals(truststorePath.toString(), props["database.ssl.truststore"])
            Assertions.assertEquals("trust-pass", props["database.ssl.truststore.password"])
            Assertions.assertEquals(keystorePath.toString(), props["database.ssl.keystore"])
            Assertions.assertEquals("client-pass", props["database.ssl.keystore.password"])

            // The JDBC-prefixed properties must continue to be set so Debezium's snapshot
            // connection (which goes through the MySQL JDBC driver) keeps working.
            Assertions.assertEquals("verify_ca", props["database.sslMode"])
            Assertions.assertEquals(
                truststorePath.toUri().toString(),
                props["database.trustCertificateKeyStoreUrl"],
            )
            Assertions.assertEquals(
                keystorePath.toUri().toString(),
                props["database.clientCertificateKeyStoreUrl"],
            )
        } finally {
            Files.deleteIfExists(truststorePath)
            Files.deleteIfExists(keystorePath)
        }
    }

    /**
     * `verify_ca` without client certificates (CA-only trust): only the truststore properties
     * should be set, and no keystore properties should leak.
     */
    @Test
    fun verifyCaWithoutClientCertOnlySetsTruststore() {
        val truststorePath: Path = Files.createTempFile("source-mysql-truststore", ".p12")
        try {
            val jdbcProperties: Map<String, String> =
                mapOf(
                    MySqlSourceConfigurationFactory.SSL_MODE to "verify_ca",
                    MySqlSourceConfigurationFactory.TRUST_KEY_STORE_URL to
                        truststorePath.toUri().toString(),
                    MySqlSourceConfigurationFactory.TRUST_KEY_STORE_PASS to "trust-pass",
                    MySqlSourceConfigurationFactory.TRUST_KEY_STORE_TYPE to
                        MySqlSourceConfigurationFactory.KEY_STORE_TYPE_PKCS12,
                )

            val builder = DebeziumPropertiesBuilder().withDatabase(jdbcProperties)
            addDebeziumSslPropertiesFromJdbcProperties(builder, jdbcProperties)
            val props: Map<String, String> = builder.buildMap()

            Assertions.assertEquals("verify_ca", props["database.ssl.mode"])
            Assertions.assertEquals(truststorePath.toString(), props["database.ssl.truststore"])
            Assertions.assertEquals("trust-pass", props["database.ssl.truststore.password"])
            Assertions.assertNull(props["database.ssl.keystore"])
            Assertions.assertNull(props["database.ssl.keystore.password"])
        } finally {
            Files.deleteIfExists(truststorePath)
        }
    }

    /**
     * `required` SSL mode without any certs: only the SSL mode itself should be propagated to
     * Debezium; no truststore or keystore properties should be set.
     */
    @Test
    fun requiredSslModeOnlySetsMode() {
        val jdbcProperties: Map<String, String> =
            mapOf(MySqlSourceConfigurationFactory.SSL_MODE to "required")

        val builder = DebeziumPropertiesBuilder().withDatabase(jdbcProperties)
        addDebeziumSslPropertiesFromJdbcProperties(builder, jdbcProperties)
        val props: Map<String, String> = builder.buildMap()

        Assertions.assertEquals("required", props["database.ssl.mode"])
        Assertions.assertNull(props["database.ssl.truststore"])
        Assertions.assertNull(props["database.ssl.truststore.password"])
        Assertions.assertNull(props["database.ssl.keystore"])
        Assertions.assertNull(props["database.ssl.keystore.password"])
    }

    /** Empty JDBC properties: no Debezium SSL properties should be added. */
    @Test
    fun noJdbcSslPropertiesAddsNothing() {
        val builder = DebeziumPropertiesBuilder()
        addDebeziumSslPropertiesFromJdbcProperties(builder, emptyMap())
        val props: Map<String, String> = builder.buildMap()

        Assertions.assertNull(props["database.ssl.mode"])
        Assertions.assertNull(props["database.ssl.truststore"])
        Assertions.assertNull(props["database.ssl.keystore"])
    }
}
