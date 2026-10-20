/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

import io.airbyte.cdk.h2.H2TestFixture
import io.airbyte.cdk.h2source.H2SourceConfigurationFactory
import io.airbyte.cdk.h2source.H2SourceConfigurationSpecification
import io.airbyte.cdk.ssh.SshBastionContainer
import io.airbyte.cdk.testcontainers.DOCKER_HOST_FROM_WITHIN_CONTAINER
import org.apache.logging.log4j.LogManager
import org.apache.logging.log4j.core.LogEvent
import org.apache.logging.log4j.core.Logger
import org.apache.logging.log4j.core.appender.AbstractAppender
import org.apache.logging.log4j.core.config.Property
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.testcontainers.Testcontainers

class JdbcConnectionFactoryTest {
    val h2 = H2TestFixture()

    init {
        Testcontainers.exposeHostPorts(h2.port)
    }

    val sshBastion = SshBastionContainer(tunnelingToHostPort = h2.port)

    @Test
    fun testVanilla() {
        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
            }
        val factory = JdbcConnectionFactory(H2SourceConfigurationFactory().make(configPojo))
        Assertions.assertEquals("H2", factory.get().metaData.databaseProductName)
    }

    @Test
    fun testConnectionLogRedactsCredentials() {
        val logger = LogManager.getLogger(JdbcConnectionFactory::class.java) as Logger
        val appender =
            object :
                AbstractAppender(
                    "JdbcConnectionFactoryTest",
                    null,
                    null,
                    false,
                    Property.EMPTY_ARRAY,
                ) {
                val messages = mutableListOf<String>()

                override fun append(event: LogEvent) {
                    messages.add(event.message.formattedMessage)
                }
            }
        appender.start()
        logger.addAppender(appender)

        try {
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                }
            val config = H2SourceConfigurationFactory().make(configPojo)
            val configWithSecret =
                config.copy(
                    jdbcUrlFmt =
                        "${config.jdbcUrlFmt};CustomProperties=(AccountID=TSTACCT;OAuth2Token=fake-oauth2-token-value)",
                )

            runCatching { JdbcConnectionFactory(configWithSecret).get() }

            Assertions.assertTrue(appender.messages.any { it.contains("Creating new connection") })
            val message = appender.messages.single { it.contains("Creating new connection") }
            Assertions.assertFalse(message.contains("fake-oauth2-token-value"))
            Assertions.assertTrue(message.contains("OAuth2Token=****"))
        } finally {
            logger.removeAppender(appender)
            appender.stop()
        }
    }

    @Test
    fun testSshKeyAuth() {
        val configPojo =
            H2SourceConfigurationSpecification().apply {
                host = DOCKER_HOST_FROM_WITHIN_CONTAINER // required only because of container
                port = h2.port
                database = h2.database
                setTunnelMethodValue(sshBastion.outerKeyAuthTunnelMethod)
            }
        val factory = JdbcConnectionFactory(H2SourceConfigurationFactory().make(configPojo))
        Assertions.assertEquals("H2", factory.get().metaData.databaseProductName)
    }

    @Test
    fun testSshPasswordAuth() {
        val configPojo =
            H2SourceConfigurationSpecification().apply {
                host = DOCKER_HOST_FROM_WITHIN_CONTAINER // required only because of container
                port = h2.port
                database = h2.database
                setTunnelMethodValue(sshBastion.outerPasswordAuthTunnelMethod)
            }
        val factory = JdbcConnectionFactory(H2SourceConfigurationFactory().make(configPojo))
        Assertions.assertEquals("H2", factory.get().metaData.databaseProductName)
    }
}
