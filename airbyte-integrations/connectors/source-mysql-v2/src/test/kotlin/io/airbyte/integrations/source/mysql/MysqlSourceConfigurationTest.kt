/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MysqlSourceConfigurationTest {
    @Inject
    lateinit var pojoSupplier: ConfigurationJsonObjectSupplier<MysqlSourceConfigurationJsonObject>

    @Inject
    lateinit var factory:
        SourceConfigurationFactory<MysqlSourceConfigurationJsonObject, MysqlSourceConfiguration>

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG)
    fun testParseJdbcParameters() {
        val pojo: MysqlSourceConfigurationJsonObject = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals(config.realHost, "localhost")
        Assertions.assertEquals(config.realPort, 12345)
        Assertions.assertEquals(config.namespaces, setOf("FOO", "SYSTEM"))

        Assertions.assertEquals(config.jdbcProperties["user"], "FOO")
        Assertions.assertEquals(config.jdbcProperties["password"], "BAR")

        // Make sure we don't accidentally drop the following hardcoded settings for mysql.
        Assertions.assertEquals(config.jdbcProperties["useCursorFetch"], "true")
        Assertions.assertEquals(config.jdbcProperties["sessionVariables"], "autocommit=0")

        Assertions.assertEquals(config.jdbcProperties["foo"], "bar")

        Assertions.assertEquals(config.jdbcProperties["theAnswerToLiveAndEverything"], "42")
        Assertions.assertEquals(config.jdbcProperties["foo"], "bar")
    }
}

const val CONFIG: String =
    """
{
  "host": "localhost",
  "port": 12345,
  "username": "FOO",
  "password": "BAR",
  "schemas": [
    "FOO",
    "SYSTEM"
  ],
  "encryption": {
    "encryption_method": "preferred"
  },
  "tunnel_method": {
    "tunnel_method": "SSH_PASSWORD_AUTH",
    "tunnel_host": "localhost",
    "tunnel_port": 2222,
    "tunnel_user": "sshuser",
    "tunnel_user_password": "***"
  },
  "cursor": {
    "cursor_method": "user_defined"
  },
  "checkpoint_target_interval_seconds": 60,
  "jdbc_url_params": "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&",
  "concurrency": 2
}
"""
