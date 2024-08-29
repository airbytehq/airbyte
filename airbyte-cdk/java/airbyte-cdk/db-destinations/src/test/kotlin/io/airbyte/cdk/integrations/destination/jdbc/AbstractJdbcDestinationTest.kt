/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock

class AbstractJdbcDestinationTest {
    private fun buildConfigNoJdbcParameters(): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                "localhost",
                JdbcUtils.PORT_KEY,
                1337,
                JdbcUtils.USERNAME_KEY,
                "user",
                JdbcUtils.DATABASE_KEY,
                "db"
            )
        )
    }

    private fun buildConfigWithExtraJdbcParameters(extraParam: String): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                "localhost",
                JdbcUtils.PORT_KEY,
                1337,
                JdbcUtils.USERNAME_KEY,
                "user",
                JdbcUtils.DATABASE_KEY,
                "db",
                JdbcUtils.JDBC_URL_PARAMS_KEY,
                extraParam
            )
        )
    }

    @Test
    fun testNoExtraParamsNoDefault() {
        val connectionProperties =
            TestJdbcDestination().getConnectionProperties(buildConfigNoJdbcParameters())

        val expectedProperties: Map<String, String> = ImmutableMap.of()
        Assertions.assertEquals(expectedProperties, connectionProperties)
    }

    @Test
    fun testNoExtraParamsWithDefault() {
        val defaultProperties: Map<String, String> = ImmutableMap.of("A_PARAMETER", "A_VALUE")

        val connectionProperties =
            TestJdbcDestination(defaultProperties)
                .getConnectionProperties(buildConfigNoJdbcParameters())

        Assertions.assertEquals(defaultProperties, connectionProperties)
    }

    @Test
    fun testExtraParamNoDefault() {
        val extraParam = "key1=value1&key2=value2&key3=value3"
        val connectionProperties =
            TestJdbcDestination()
                .getConnectionProperties(buildConfigWithExtraJdbcParameters(extraParam))
        val expectedProperties: Map<String, String> =
            ImmutableMap.of("key1", "value1", "key2", "value2", "key3", "value3")
        Assertions.assertEquals(expectedProperties, connectionProperties)
    }

    @Test
    fun testExtraParamWithDefault() {
        val defaultProperties: Map<String, String> = ImmutableMap.of("A_PARAMETER", "A_VALUE")
        val extraParam = "key1=value1&key2=value2&key3=value3"
        val connectionProperties =
            TestJdbcDestination(defaultProperties)
                .getConnectionProperties(buildConfigWithExtraJdbcParameters(extraParam))
        val expectedProperties: Map<String, String> =
            ImmutableMap.of(
                "A_PARAMETER",
                "A_VALUE",
                "key1",
                "value1",
                "key2",
                "value2",
                "key3",
                "value3"
            )
        Assertions.assertEquals(expectedProperties, connectionProperties)
    }

    @Test
    fun testExtraParameterEqualToDefault() {
        val defaultProperties: Map<String, String> = ImmutableMap.of("key1", "value1")
        val extraParam = "key1=value1&key2=value2&key3=value3"
        val connectionProperties =
            TestJdbcDestination(defaultProperties)
                .getConnectionProperties(buildConfigWithExtraJdbcParameters(extraParam))
        val expectedProperties: Map<String, String> =
            ImmutableMap.of("key1", "value1", "key2", "value2", "key3", "value3")
        Assertions.assertEquals(expectedProperties, connectionProperties)
    }

    @Test
    fun testExtraParameterDiffersFromDefault() {
        val defaultProperties: Map<String, String> = ImmutableMap.of("key1", "value0")
        val extraParam = "key1=value1&key2=value2&key3=value3"

        Assertions.assertThrows(IllegalArgumentException::class.java) {
            TestJdbcDestination(defaultProperties)
                .getConnectionProperties(buildConfigWithExtraJdbcParameters(extraParam))
        }
    }

    @Test
    fun testInvalidExtraParam() {
        val extraParam = "key1=value1&sdf&"
        Assertions.assertThrows(ConfigErrorException::class.java) {
            TestJdbcDestination()
                .getConnectionProperties(buildConfigWithExtraJdbcParameters(extraParam))
        }
    }

    internal class TestJdbcDestination
    @JvmOverloads
    constructor(private val defaultProperties: Map<String, String> = HashMap()) :
        AbstractJdbcDestination<MinimumDestinationState.Impl>(
            "",
            StandardNameTransformer(),
            TestJdbcSqlOperations()
        ) {
        override fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
            return defaultProperties
        }

        override fun toJdbcConfig(config: JsonNode): JsonNode {
            return config
        }

        override fun getSqlGenerator(config: JsonNode): JdbcSqlGenerator = mock()

        override fun getDestinationHandler(
            databaseName: String,
            database: JdbcDatabase,
            rawTableSchema: String
        ): JdbcDestinationHandler<MinimumDestinationState.Impl> {
            return mock()
        }

        override fun getMigrations(
            database: JdbcDatabase,
            databaseName: String,
            sqlGenerator: SqlGenerator,
            destinationHandler: DestinationHandler<MinimumDestinationState.Impl>
        ): List<Migration<MinimumDestinationState.Impl>> {
            return emptyList()
        }

        public override fun getConnectionProperties(config: JsonNode): Map<String, String> =
            super.getConnectionProperties(config)
    }
}
