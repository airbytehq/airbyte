/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.AIRBYTE_CLOUD_ENV
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.output.sockets.MEDIUM_PROPERTY
import io.airbyte.cdk.output.sockets.SOCKET_PATHS_PROPERTY
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.net.URI
import java.nio.file.Files
import java.nio.file.Path
import java.time.Duration
import javax.net.ssl.SSLContext
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST, AIRBYTE_CLOUD_ENV], rebuildContext = true)
class MySqlSourceConfigurationTest {
    @Inject
    lateinit var pojoSupplier:
        ConfigurationSpecificationSupplier<MySqlSourceConfigurationSpecification>

    @Inject
    lateinit var factory:
        SourceConfigurationFactory<MySqlSourceConfigurationSpecification, MySqlSourceConfiguration>

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(
        name = "airbyte.connector.config.jdbc_url_params",
        value = "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&"
    )
    fun testParseJdbcParameters() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals(config.realHost, "localhost")
        Assertions.assertEquals(config.realPort, 12345)
        Assertions.assertEquals(config.namespaces, setOf("SYSTEM"))
        Assertions.assertTrue(config.sshTunnel is SshNoTunnelMethod)

        Assertions.assertEquals(config.jdbcProperties["user"], "FOO")
        Assertions.assertEquals(config.jdbcProperties["password"], "BAR")

        // Make sure we don't accidentally drop the following hardcoded settings for mysql.
        Assertions.assertEquals(config.jdbcProperties["useCursorFetch"], "true")
        Assertions.assertEquals(config.jdbcProperties["sessionVariables"], "autocommit=0")

        Assertions.assertEquals(config.jdbcProperties["theAnswerToLiveAndEverything"], "42")
        Assertions.assertEquals(config.jdbcProperties["foo"], "bar")
        // test default value
        Assertions.assertEquals(config.jdbcProperties["sslMode"], "required")
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(name = "airbyte.connector.config.json", value = CONFIG_V1)
    fun testParseConfigFromV1() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals(config.realHost, "localhost")
        Assertions.assertEquals(config.realPort, 12345)
        Assertions.assertEquals(config.namespaces, setOf("SYSTEM"))

        Assertions.assertEquals(config.jdbcProperties["user"], "FOO")
        Assertions.assertEquals(config.jdbcProperties["password"], "BAR")
        Assertions.assertEquals(config.jdbcProperties["sslMode"], "required")
        Assertions.assertTrue(config.incrementalConfiguration is CdcIncrementalConfiguration)

        val cdcCursor = config.incrementalConfiguration as CdcIncrementalConfiguration

        Assertions.assertEquals(cdcCursor.initialLoadTimeout, Duration.ofHours(9))
        Assertions.assertEquals(
            cdcCursor.invalidCdcCursorPositionBehavior,
            InvalidCdcCursorPositionBehavior.RESET_SYNC
        )

        Assertions.assertTrue(config.sshTunnel is SshNoTunnelMethod)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(name = "airbyte.connector.config.json", value = CONFIG_V2)
    fun testCloudRequirements() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        try {
            factory.makeWithoutExceptionHandling(pojo)
            // If we reach here, no exception was thrown - test should fail
            Assertions.fail("Expected ConfigErrorException, but no exception was thrown")
        } catch (e: ConfigErrorException) {
            // Here we verify that the caught exception has the expected message
            Assertions.assertEquals(
                "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel.",
                e.message
            )
        }
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(name = "airbyte.connector.config.concurrency", value = "5")
    @Property(name = "airbyte.connector.config.max_db_connections", value = "2")
    @Property(
        name = "airbyte.connector.config.jdbc_url_params",
        value = "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&"
    )
    fun testConcurrencySettingMigrationLegacyMode() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)
        Assertions.assertEquals(2, config.maxConcurrency)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(
        name = "airbyte.connector.config.jdbc_url_params",
        value = "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&"
    )
    @Property(name = MEDIUM_PROPERTY, value = "SOCKET")
    @Property(name = SOCKET_PATHS_PROPERTY, value = "a,b,c")
    @Property(name = "airbyte.connector.config.concurrency", value = "1")
    fun testConcurrencySettingMigrationSocketMode() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)
        Assertions.assertEquals(3, config.maxConcurrency)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(
        name = "airbyte.connector.config.jdbc_url_params",
        value = "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&"
    )
    @Property(name = MEDIUM_PROPERTY, value = "SOCKET")
    @Property(name = SOCKET_PATHS_PROPERTY, value = "a,b,c")
    @Property(name = "airbyte.connector.config.concurrency", value = "5")
    //    @Property(name = "airbyte.connector.config.max_db_connections", value = "2")
    fun testConcurrencySettingMigrationSocketModeBackwardCompatibility() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)
        Assertions.assertEquals(5, config.maxConcurrency)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(
        name = "airbyte.connector.config.jdbc_url_params",
        value = "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&"
    )
    @Property(name = MEDIUM_PROPERTY, value = "SOCKET")
    @Property(name = SOCKET_PATHS_PROPERTY, value = "a,b,c")
    @Property(name = "airbyte.connector.config.concurrency", value = "5")
    @Property(name = "airbyte.connector.config.max_db_connections", value = "4")
    fun testConcurrencySettingMigrationSocketModeOverride() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)
        Assertions.assertEquals(4, config.maxConcurrency)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(name = "airbyte.connector.config.json", value = CONFIG_VERIFY_CA_WITH_CLIENT_CERT)
    fun testDebeziumSslPropertiesForVerifyCaWithClientCert() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        // JDBC SSL properties are unchanged.
        Assertions.assertEquals("verify_ca", config.jdbcProperties["sslMode"])
        Assertions.assertNotNull(config.jdbcProperties["trustCertificateKeyStoreUrl"])
        Assertions.assertNotNull(config.jdbcProperties["clientCertificateKeyStoreUrl"])

        val truststorePath: String =
            Path.of(URI.create(config.jdbcProperties["trustCertificateKeyStoreUrl"])).toString()
        Assertions.assertEquals("verify_ca", config.debeziumSslProperties["ssl.mode"])
        Assertions.assertEquals(truststorePath, config.debeziumSslProperties["ssl.truststore"])
        Assertions.assertTrue(Files.exists(Path.of(truststorePath)))
        Assertions.assertEquals(
            "client-pass",
            config.debeziumSslProperties["ssl.truststore.password"]
        )

        val keystorePath: String =
            Path.of(URI.create(config.jdbcProperties["clientCertificateKeyStoreUrl"])).toString()
        Assertions.assertEquals(keystorePath, config.debeziumSslProperties["ssl.keystore"])
        Assertions.assertTrue(Files.exists(Path.of(keystorePath)))
        Assertions.assertEquals(
            "client-pass",
            config.debeziumSslProperties["ssl.keystore.password"]
        )
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(name = "airbyte.connector.config.json", value = CONFIG_VERIFY_CA_WITHOUT_CLIENT_CERT)
    fun testDebeziumSslPropertiesForVerifyCaWithoutClientCert() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals("verify_ca", config.debeziumSslProperties["ssl.mode"])

        val truststorePath: String =
            Path.of(URI.create(config.jdbcProperties["trustCertificateKeyStoreUrl"])).toString()
        Assertions.assertEquals(truststorePath, config.debeziumSslProperties["ssl.truststore"])
        Assertions.assertTrue(Files.exists(Path.of(truststorePath)))
        Assertions.assertFalse(
            config.debeziumSslProperties["ssl.truststore.password"].isNullOrBlank()
        )

        Assertions.assertNull(config.debeziumSslProperties["ssl.keystore"])
        Assertions.assertNull(config.debeziumSslProperties["ssl.keystore.password"])
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(name = "airbyte.connector.config.json", value = CONFIG_V1)
    fun testDebeziumSslPropertiesForRequired() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals(mapOf("ssl.mode" to "required"), config.debeziumSslProperties)
    }

    @Test
    fun testTls() {
        val context = SSLContext.getDefault()
        val supported = context.supportedSSLParameters.protocols
        val enabled = context.defaultSSLParameters.protocols

        println("Supported TLS versions: ${supported.joinToString()}")
        println("Enabled TLS versions: ${enabled.joinToString()}")
    }

    companion object {

        const val CONFIG_V1: String =
            """
{
  "host": "localhost",
  "port": 12345,
  "database": "SYSTEM",
  "password": "BAR",
  "ssl_mode": {
    "mode": "required"
  },
  "username": "FOO",
  "tunnel_method": {
    "tunnel_method": "NO_TUNNEL"
  },
  "replication_method": {
    "method": "CDC",
    "initial_waiting_seconds": 301,
    "initial_load_timeout_hours": 9,
    "invalid_cdc_cursor_position_behavior": "Re-sync data"
  }
}
"""
        const val CONFIG_V2: String =
            """
{
  "host": "localhost",
  "port": 12345,
  "database": "SYSTEM",
  "password": "BAR",
  "ssl_mode": {
    "mode": "preferred"
  },
  "username": "FOO",
  "tunnel_method": {
    "tunnel_method": "NO_TUNNEL"
  },
  "replication_method": {
    "method": "CDC",
    "initial_waiting_seconds": 301,
    "initial_load_timeout_hours": 9,
    "invalid_cdc_cursor_position_behavior": "Re-sync data"
  }
}
"""

        const val CA_PEM: String =
            "-----BEGIN CERTIFICATE-----\\n" +
                "MIIDAzCCAeugAwIBAgIBATANBgkqhkiG9w0BAQsFADA8MTowOAYDVQQDDDFNeVNR\\n" +
                "TF9TZXJ2ZXJfOC4wLjMwX0F1dG9fR2VuZXJhdGVkX0NBX0NlcnRpZmljYXRlMB4X\\n" +
                "DTIyMDgwODA1NDMwOFoXDTMyMDgwNTA1NDMwOFowPDE6MDgGA1UEAwwxTXlTUUxf\\n" +
                "U2VydmVyXzguMC4zMF9BdXRvX0dlbmVyYXRlZF9DQV9DZXJ0aWZpY2F0ZTCCASIw\\n" +
                "DQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKb2tDaE4TO/4xKRZ0QqpB4ho3cy\\n" +
                "daw85Sn8VNLa42EJgZVpSr0WCFl11Go7r0O2TMvceaWsnJU7FLhYHSR+Dlm62yVO\\n" +
                "0DsnMOC0kUoDnjSE/PmponWnoC79fgXV7AwKxSW4LLxYlPHQb4Kb7rv+UJ3KbxZz\\n" +
                "zB7JEm9WQCJ/byn1/jxQtoPGvWL2csX3RFr9QNh8UgpOBQsbebeLWNgxdYda2sz3\\n" +
                "kJcwk754Vj1mx6iszjLP0oHZu+RuoM+xIrpDmpPNMW/0rQl6q+vCymNxaxX8+MuW\\n" +
                "czRJ1hjh4cVjArp8YhJCEMVaLajVkhbzYaPRsdW1NGjh+C3eZnOm5fRi35kCAwEA\\n" +
                "AaMQMA4wDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAWKlbtUosXVy7\\n" +
                "LbFEuL3c2Igs023v0mQNvtZVBl5Qpsxpc3+ybmQfksEQoPxPKmWpsnWv5Bsvt335\\n" +
                "/NHv1wSajHEpoyDBtF1QT2rR/kjezFpiH9AY3xwtBdZhTDlc5UBrpyv+Issn1CZF\\n" +
                "edcIk54Gzxifn+Et5WP8b6HV/ehdE0qQPtHDmendEaIHXg12/NE+hj3DocSVm8w/\\n" +
                "LUNeYd9wXefwMrEWwDn0DZSsShZmgJoppA15qOnq+FVW/bhZwRv5L4l3AJv0SGoA\\n" +
                "o7DXxD0VGHDA6aC4tJssZbrnoDCBPzYmt9s9GwVupuEroJHZ0Wks4pt4Wx50DUgA\\n" +
                "KC3v0Mo/gg==\\n" +
                "-----END CERTIFICATE-----\\n"

        const val CLIENT_CERT_PEM: String =
            "-----BEGIN CERTIFICATE-----\\n" +
                "MIIDBDCCAeygAwIBAgIBAzANBgkqhkiG9w0BAQsFADA8MTowOAYDVQQDDDFNeVNR\\n" +
                "TF9TZXJ2ZXJfOC4wLjMwX0F1dG9fR2VuZXJhdGVkX0NBX0NlcnRpZmljYXRlMB4X\\n" +
                "DTIyMDgwODA1NDMwOFoXDTMyMDgwNTA1NDMwOFowQDE+MDwGA1UEAww1TXlTUUxf\\n" +
                "U2VydmVyXzguMC4zMF9BdXRvX0dlbmVyYXRlZF9DbGllbnRfQ2VydGlmaWNhdGUw\\n" +
                "ggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCV/eRPDZmrPP8d2pKsFizU\\n" +
                "JQkGOYDKXOilLibR1TQwN/8MToop8+mvtMi7zr/cWBDR0qTObbduWFQdK82vGppS\\n" +
                "ZgrRG3QWVpe8NNI9AhriVZiOmcEQqgAhbgos57Tkjy3qghNbUN1KGb3I0DnNOtvF\\n" +
                "RIdATbE+LxOTgCzz/Cw6DVReunQvVo9T4EC4PBBUelMWlAJLo61AQVLM3ufx4ug2\\n" +
                "1wbV6D/aSRooNhkwWcwk+2vabxKnOzFAQzNU7dIZlBpo6coHFwZDUxtdM2DtuLHn\\n" +
                "/r9CsMw8p4wtdIRXrTDmiF/xTXKnABGM8kEqPovZ6eh7He1jrzLTVANUfNQc5b8F\\n" +
                "AgMBAAGjDTALMAkGA1UdEwQCMAAwDQYJKoZIhvcNAQELBQADggEBAGDJ6XgLBzat\\n" +
                "rpLDfGHR/tZ4eFzt1Nhjzl4CyFjpUcr2e2K5XmuveJAecaQSHff2zXwfGpg/BIen\\n" +
                "WcPm2daIzcfN/wWg8ENMB/JE3dMq44pOmWs2g4FPDQuaH81IV0hGX4klk2XZpskJ\\n" +
                "moWXyGY43Xr3bbNBjyOxgBsQc4kD96ODMUKfzNMH4p9hXKAMrF9DqHwQUho5uM6M\\n" +
                "RnU7Uzr745xw7LKJglCgO20t4302wzsUAEPuCTcB9wJy1/cRbMmoLAdUdn6XhFb4\\n" +
                "pR3UDNJvXGc8by6VWrXOeB0BFeB3beMxezlTHDOWoWeJwvEfAAD/dpwHXwp5dm9L\\n" +
                "VjtlERcTfH8=\\n" +
                "-----END CERTIFICATE-----\\n"

        const val CLIENT_KEY_PEM: String =
            "-----BEGIN RSA PRIVATE KEY-----\\n" +
                "MIIEowIBAAKCAQEAlf3kTw2Zqzz/HdqSrBYs1CUJBjmAylzopS4m0dU0MDf/DE6K\\n" +
                "KfPpr7TIu86/3FgQ0dKkzm23blhUHSvNrxqaUmYK0Rt0FlaXvDTSPQIa4lWYjpnB\\n" +
                "EKoAIW4KLOe05I8t6oITW1DdShm9yNA5zTrbxUSHQE2xPi8Tk4As8/wsOg1UXrp0\\n" +
                "L1aPU+BAuDwQVHpTFpQCS6OtQEFSzN7n8eLoNtcG1eg/2kkaKDYZMFnMJPtr2m8S\\n" +
                "pzsxQEMzVO3SGZQaaOnKBxcGQ1MbXTNg7bix5/6/QrDMPKeMLXSEV60w5ohf8U1y\\n" +
                "pwARjPJBKj6L2enoex3tY68y01QDVHzUHOW/BQIDAQABAoIBAHk/CHyC4PKUVyHZ\\n" +
                "2vCy6EABRB89AogSvJkyCn1anFpSGaDoKDWrjv7S4+U1RtCme8oxPboE5N+VFUGT\\n" +
                "dCwVFCSBikLor1mTXAruo/hfKD5HtQ+o6HFBCuP7IMyV7RtJRnOn/F+3qXpJ/qlC\\n" +
                "8UaeSqNXNwHbC+jZgzibxzrfYRz3BqnBYZsSP7/piN+rk6vAGs7WeawO1adqsLS6\\n" +
                "Hr9GilEe+bW/CtXsah3AYVwxDnwo/c03JYBdzYkRRqLgJ9dDG/5o/88FeeKbVb+U\\n" +
                "ZrGV9adwa+KGwsuMTYi7pkXUosm+43hLkmYUykxFv0vfkGz8EnDh4MBtY66QMkUJ\\n" +
                "cQgWl6ECgYEAxVJNsxpJjEa+d737iK7ylza0GhcTI3+uNPN92u0oucictMzLIm7N\\n" +
                "HAUhrHoO71NDYQYJlox7BG8mjze7l6fkwGfpg2u/KsN0vIqc+F+gIQeC7kmpRxQk\\n" +
                "l96pxMW25VhibZJFBaDx9UeBkR9RBnI1AF3jD3+wOdua+C9CMahdTDkCgYEAwph4\\n" +
                "FY2gcOSpA0Xz1cOFPNuwQhy9Lh3MJsb1kt20hlTcmpp3GpBrzyggiyIlpBtBHDrP\\n" +
                "6FcjZtV58bv8ckKB8jklvooJkyjmowBx+L7mHZ6/7QFPDQkp/dY9dQPtWjgrPyo+\\n" +
                "rLIN+SoVmyKdyXXaauyjyEPAexsuxzUKq0MMIS0CgYEAirvJQYnT+DqtJAeBWKKY\\n" +
                "kdS2YDmlDSpyU2x3KnvgTG9OLphmojkBIRhCir/uzDngf9D84Mq4m2+CzuNCk+hJ\\n" +
                "nzXwKqSQ7gIqi31xy/d/4Hklh2BnEkCJUfYNqvnQFARGf/99Y+268Ndrs5svHrch\\n" +
                "qLZaNMV0I9nRZXnksoFLx5ECgYBJ8LFAT041V005Jy1dfit0Um2I0W64xS27VkId\\n" +
                "igx8NmaUgDjdaR7t2etzsofm8UwuM9KoD+QtwNPTHIDx0X+a0EgdPEojFpl8OkEU\\n" +
                "KUU64AVBQwwMgfzorK0xd0qKy2jzWVPzPry8flczWVXnJNbXZg9dmxDaNhvyKZ9i\\n" +
                "L9m+CQKBgG3kkQTtsT7k1kQt/6cqjAaBq9Koi0gbS8hWjTioqPKHVQAAEjqVkmqa\\n" +
                "uuD/3Knh1gCgxW4jAUokRwfM7IgVA/plQQDQaKBzcFUl94Hl+t6VuvdvtA02MboE\\n" +
                "7TicEc38QKFoLN2hti0Bmm1eJCionsSPiuyDYH5XnhSz7TDjV9sM\\n" +
                "-----END RSA PRIVATE KEY-----\\n"

        const val CONFIG_VERIFY_CA_WITH_CLIENT_CERT: String =
            "{\"host\":\"localhost\",\"port\":12345,\"database\":\"SYSTEM\",\"password\":\"BAR\",\"username\":\"FOO\"," +
                "\"tunnel_method\":{\"tunnel_method\":\"NO_TUNNEL\"}," +
                "\"replication_method\":{\"method\":\"CDC\",\"initial_waiting_seconds\":301," +
                "\"initial_load_timeout_hours\":9," +
                "\"invalid_cdc_cursor_position_behavior\":\"Re-sync data\"}," +
                "\"ssl_mode\":{\"mode\":\"verify_ca\",\"ca_certificate\":\"" +
                CA_PEM +
                "\",\"client_certificate\":\"" +
                CLIENT_CERT_PEM +
                "\",\"client_key\":\"" +
                CLIENT_KEY_PEM +
                "\",\"client_key_password\":\"client-pass\"}}"

        const val CONFIG_VERIFY_CA_WITHOUT_CLIENT_CERT: String =
            "{\"host\":\"localhost\",\"port\":12345,\"database\":\"SYSTEM\",\"password\":\"BAR\",\"username\":\"FOO\"," +
                "\"tunnel_method\":{\"tunnel_method\":\"NO_TUNNEL\"}," +
                "\"replication_method\":{\"method\":\"CDC\",\"initial_waiting_seconds\":301," +
                "\"initial_load_timeout_hours\":9," +
                "\"invalid_cdc_cursor_position_behavior\":\"Re-sync data\"}," +
                "\"ssl_mode\":{\"mode\":\"verify_ca\",\"ca_certificate\":\"" +
                CA_PEM +
                "\"}}"
    }
}
