/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.OracleContainer

class OracleSourceConfigurationIntegrationTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }

    @Test
    fun testCheckNneSuccess() {
        val configSpec: OracleSourceConfigurationSpecification =
            OracleContainerFactory.configSpecification(dbContainer).also {
                val encryption = EncryptionAlgorithm()
                encryption.encryptionAlgorithm = "AES128"
                it.setEncryptionValue(encryption)
            }
        val config: OracleSourceConfiguration = OracleSourceConfigurationFactory().make(configSpec)
        Assertions.assertTrue("oracle.net.encryption_client" in config.jdbcProperties)
        Assertions.assertTrue("oracle.net.encryption_types_client" in config.jdbcProperties)
        Assertions.assertDoesNotThrow { JdbcConnectionFactory(config).get() }
        SyncsTestFixture.testCheck(configSpec, expectedFailure = "Discovered zero tables")
    }

    @Test
    fun testCheckNneFailure() {
        val configSpec: OracleSourceConfigurationSpecification =
            OracleContainerFactory.configSpecification(dbContainer).also {
                val encryption = EncryptionAlgorithm()
                // Use an encryption algorithm which, while valid according to the config spec,
                // is not supported by the database instance in the testcontainer.
                encryption.encryptionAlgorithm = "3DES112"
                it.setEncryptionValue(encryption)
            }
        SyncsTestFixture.testCheck(configSpec, expectedFailure = "ORA-18903")
    }

    @Test
    fun testCheckSsl() {
        val configSpec: OracleSourceConfigurationSpecification =
            OracleContainerFactory.configSpecification(dbContainer).also {
                OracleContainerFactory.WithSslAndNne.decorateWithSSL(it, dbContainer)
            }
        val config: OracleSourceConfiguration = OracleSourceConfigurationFactory().make(configSpec)
        Assertions.assertNotEquals(dbContainer.getMappedPort(1521), configSpec.port)
        Assertions.assertFalse("javax.net.ssl.keyStore" in config.jdbcProperties)
        Assertions.assertTrue("javax.net.ssl.trustStore" in config.jdbcProperties)
        Assertions.assertDoesNotThrow { JdbcConnectionFactory(config).get() }
        SyncsTestFixture.testCheck(configSpec, expectedFailure = "Discovered zero tables")
    }

    companion object {
        lateinit var dbContainer: OracleContainer

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                OracleContainerFactory.exclusive(
                    "gvenzl/oracle-free:23.6-full-faststart",
                    OracleContainerFactory.WithSslAndNne,
                )
        }
    }
}
