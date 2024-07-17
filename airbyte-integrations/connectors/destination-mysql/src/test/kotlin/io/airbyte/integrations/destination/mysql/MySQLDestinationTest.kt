/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.commons.json.Jsons.jsonNode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MySQLDestinationTest {
    private fun buildConfigNoJdbcParameters(): JsonNode {
        return jsonNode(
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
        return jsonNode(
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

    private fun buildConfigNoExtraJdbcParametersWithoutSsl(): JsonNode {
        return jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                "localhost",
                JdbcUtils.PORT_KEY,
                1337,
                JdbcUtils.USERNAME_KEY,
                "user",
                JdbcUtils.DATABASE_KEY,
                "db",
                JdbcUtils.SSL_KEY,
                false
            )
        )
    }

    @Test
    fun testNoExtraParams() {
        val config = buildConfigNoJdbcParameters()
        val jdbcConfig = MySQLDestination().toJdbcConfig(config)
        Assertions.assertEquals(JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
    }

    @Test
    fun testEmptyExtraParams() {
        val jdbcConfig = MySQLDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""))
        Assertions.assertEquals(JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
    }

    @Test
    fun testExtraParams() {
        val extraParam = "key1=value1&key2=value2&key3=value3"
        val jdbcConfig =
            MySQLDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam))
        Assertions.assertEquals(JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
    }

    @Test
    fun testDefaultParamsNoSSL() {
        val defaultProperties =
            MySQLDestination()
                .getDefaultConnectionProperties(buildConfigNoExtraJdbcParametersWithoutSsl())
        Assertions.assertEquals(MySQLDestination.DEFAULT_JDBC_PARAMETERS, defaultProperties)
    }

    @Test
    fun testDefaultParamsWithSSL() {
        val defaultProperties =
            MySQLDestination().getDefaultConnectionProperties(buildConfigNoJdbcParameters())
        Assertions.assertEquals(MySQLDestination.DEFAULT_SSL_JDBC_PARAMETERS, defaultProperties)
    }

    companion object {
        const val JDBC_URL: String = "jdbc:mysql://localhost:1337"
    }
}
