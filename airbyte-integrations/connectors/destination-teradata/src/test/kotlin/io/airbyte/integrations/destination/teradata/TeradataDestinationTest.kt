/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.map.MoreMaps
import io.airbyte.integrations.destination.teradata.util.TeradataConstants
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class TeradataDestinationTest {

    private lateinit var config: JsonNode
    private val destination = TeradataDestination()

    private val EXPECTED_JDBC_URL = "jdbc:teradata://localhost/"

    private val EXTRA_JDBC_PARAMS = "key1=value1&key2=value2&key3=value3"

    private fun getUserName(): String {
        return config.get(JdbcUtils.USERNAME_KEY).asText()
    }

    private fun getPassword(): String {
        return config.get(JdbcUtils.PASSWORD_KEY).asText()
    }

    private fun getHostName(): String {
        return config.get(JdbcUtils.HOST_KEY).asText()
    }

    private fun getSchemaName(): String {
        return config.get(JdbcUtils.SCHEMA_KEY).asText()
    }

    @BeforeEach
    fun setup() {
        this.config = createConfig()
    }

    private fun createConfig(): JsonNode {
        return Jsons.jsonNode(baseParameters())
    }

    private fun createConfig(sslEnable: Boolean): JsonNode {
        val jsonNode: JsonNode
        if (sslEnable) {
            jsonNode = Jsons.jsonNode(sslBaseParameters())
        } else {
            jsonNode = createConfig()
        }
        return jsonNode
    }

    private fun createConfig(sslMethod: String): JsonNode {
        val additionalParameters: Map<String, Any> = getAdditionalParams(sslMethod)
        return Jsons.jsonNode(MoreMaps.merge(sslBaseParameters(), additionalParameters))
    }

    private fun getAdditionalParams(sslMethod: String): Map<String, Any> {
        val additionalParameters: Map<String, Any> =
            when (sslMethod) {
                "verify-ca",
                "verify-full" -> {
                    ImmutableMap.of(
                        TeradataConstants.PARAM_SSL_MODE,
                        Jsons.jsonNode(
                            ImmutableMap.of(
                                TeradataConstants.PARAM_MODE,
                                sslMethod,
                                TeradataConstants.CA_CERT_KEY,
                                "dummycertificatecontent"
                            )
                        )
                    )
                }
                else -> {
                    ImmutableMap.of(
                        TeradataConstants.PARAM_SSL_MODE,
                        Jsons.jsonNode(ImmutableMap.of(TeradataConstants.PARAM_MODE, sslMethod))
                    )
                }
            }
        return additionalParameters
    }

    private fun getBrowserAuthParams(): Map<String, Any> {
        return ImmutableMap.builder<String, Any>()
            .put(TeradataConstants.AUTH_TYPE, "BROWSER")
            .build()
    }

    private fun getLDAPAuthParams(): Map<String, Any> {
        return ImmutableMap.builder<String, Any>()
            .put(TeradataConstants.AUTH_TYPE, "LDAP")
            .put(JdbcUtils.USERNAME_KEY, "username")
            .put(JdbcUtils.PASSWORD_KEY, "verysecure")
            .build()
    }

    private fun getTD2AuthParams(): Map<String, Any> {
        return ImmutableMap.builder<String, Any>()
            .put(TeradataConstants.AUTH_TYPE, "TD2")
            .put(JdbcUtils.USERNAME_KEY, "username")
            .put(JdbcUtils.PASSWORD_KEY, "verysecure")
            .build()
    }

    private fun baseParameters(): Map<String, Any> {
        return ImmutableMap.builder<String, Any>()
            .put(JdbcUtils.HOST_KEY, "localhost")
            .put(JdbcUtils.SCHEMA_KEY, "db")
            .put(TeradataConstants.LOG_MECH, getTD2AuthParams())
            .build()
    }

    private fun sslBaseParameters(): Map<String, Any> {
        return ImmutableMap.builder<String, Any>()
            .put(TeradataConstants.PARAM_SSL, "true")
            .put(JdbcUtils.HOST_KEY, getHostName())
            .put(JdbcUtils.SCHEMA_KEY, getSchemaName())
            .put(TeradataConstants.LOG_MECH, getTD2AuthParams())
            .build()
    }

    private fun buildConfigNoJdbcParameters(): JsonNode {
        return Jsons.jsonNode(baseParameters())
    }

    private fun buildConfigForLDAPAuth(): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                getHostName(),
                TeradataConstants.LOG_MECH,
                getLDAPAuthParams()
            )
        )
    }

    private fun buildConfigForBrowserAuth(): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                getHostName(),
                TeradataConstants.LOG_MECH,
                getBrowserAuthParams()
            )
        )
    }

    private fun buildConfigDefaultSchema(): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                getHostName(),
                TeradataConstants.LOG_MECH,
                getTD2AuthParams()
            )
        )
    }

    private fun buildConfigWithExtraJdbcParameters(extraParam: String): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                getHostName(),
                TeradataConstants.LOG_MECH,
                getTD2AuthParams(),
                JdbcUtils.SCHEMA_KEY,
                getSchemaName(),
                JdbcUtils.JDBC_URL_PARAMS_KEY,
                extraParam
            )
        )
    }

    companion object {
        @JvmStatic
        fun provideQueryBandTestCases(): Stream<Arguments> {
            return Stream.of(
                // Each test case includes the input query band and the expected result
                Arguments.of("", TeradataConstants.DEFAULT_QUERY_BAND),
                Arguments.of("    ", TeradataConstants.DEFAULT_QUERY_BAND),
                Arguments.of("appname=test", "appname=test_airbyte;org=teradata-internal-telem;"),
                Arguments.of("appname=test;", "appname=test_airbyte;org=teradata-internal-telem;"),
                Arguments.of("appname=airbyte", "appname=airbyte;org=teradata-internal-telem;"),
                Arguments.of("appname=airbyte;", "appname=airbyte;org=teradata-internal-telem;"),
                Arguments.of("org=test;", "org=test;appname=airbyte;"),
                Arguments.of("org=test", "org=test;appname=airbyte;"),
                Arguments.of("org=teradata-internal-telem", TeradataConstants.DEFAULT_QUERY_BAND),
                Arguments.of("org=teradata-internal-telem;", TeradataConstants.DEFAULT_QUERY_BAND),
                Arguments.of(
                    TeradataConstants.DEFAULT_QUERY_BAND,
                    TeradataConstants.DEFAULT_QUERY_BAND
                ),
                Arguments.of(
                    "invalid_queryband",
                    "invalid_queryband;org=teradata-internal-telem;appname=airbyte;"
                ),
                Arguments.of(
                    "org=teradata-internal-telem;appname=test;",
                    "org=teradata-internal-telem;appname=test_airbyte;"
                ),
                Arguments.of("org=custom;appname=custom;", "org=custom;appname=custom_airbyte;"),
                Arguments.of("org=custom;appname=custom", "org=custom;appname=custom_airbyte"),
                Arguments.of(
                    "org=teradata-internal-telem;appname=airbyte",
                    "org=teradata-internal-telem;appname=airbyte"
                ),
                Arguments.of(
                    "org = teradata-internal-telem;appname = airbyte",
                    "org = teradata-internal-telem;appname = airbyte"
                )
            )
        }
    }

    @Test
    fun testAuthTypeLDAPConnection() {
        val rawConfig = buildConfigForLDAPAuth()
        val jdbcConfig = destination.toJdbcConfig(rawConfig)
        val connProps: Map<String, String> = destination.getConnectionProperties(rawConfig)
        assertEquals("LDAP", connProps[TeradataConstants.LOG_MECH])
        assertEquals("username", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText())
        assertEquals("verysecure", jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText())
    }

    @Test
    fun testAuthTypeTD2Connection() {
        val rawConfig = buildConfigNoJdbcParameters()
        val jdbcConfig = destination.toJdbcConfig(rawConfig)
        val connProps: Map<String, String> = destination.getConnectionProperties(rawConfig)
        assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
        assertNull(connProps[TeradataConstants.AUTH_TYPE])
        assertEquals("username", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText())
        assertEquals("verysecure", jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText())
    }

    @Test
    fun testAuthTypeBrowserConnection() {
        val rawConfig = buildConfigForBrowserAuth()
        val jdbcConfig = destination.toJdbcConfig(rawConfig)
        val connProps: Map<String, String> = destination.getConnectionProperties(rawConfig)
        assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
        assertEquals("BROWSER", connProps[TeradataConstants.LOG_MECH])
        assertNull(jdbcConfig.get(JdbcUtils.USERNAME_KEY))
        assertNull(jdbcConfig.get(JdbcUtils.PASSWORD_KEY))
    }

    @Test
    fun testJdbcUrlAndConfigNoExtraParams() {
        val jdbcConfig = destination.toJdbcConfig(buildConfigNoJdbcParameters())
        assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
        assertEquals("db", jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText())
        assertEquals("username", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText())
        assertEquals("verysecure", jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText())
    }

    @Test
    fun testJdbcUrlEmptyExtraParams() {
        val jdbcConfig = destination.toJdbcConfig(buildConfigWithExtraJdbcParameters(""))
        assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
        assertEquals("db", jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText())
        assertEquals("username", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText())
        assertEquals("verysecure", jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText())
        assertEquals("", jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText())
    }

    @Test
    fun testJdbcUrlExtraParams() {
        val jdbcConfig =
            destination.toJdbcConfig(buildConfigWithExtraJdbcParameters(EXTRA_JDBC_PARAMS))
        assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
        assertEquals("username", jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText())
        assertEquals("db", jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText())
        assertEquals(EXTRA_JDBC_PARAMS, jdbcConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText())
    }

    @Test
    fun testDefaultSchemaName() {
        val jdbcConfig = destination.toJdbcConfig(buildConfigDefaultSchema())
        assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
        assertEquals(
            TeradataConstants.DEFAULT_SCHEMA_NAME,
            jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText()
        )
    }

    @Test
    fun testSSLDisable() {
        val jdbcConfig = createConfig(false)
        val properties: Map<String, String> = destination.getDefaultConnectionProperties(jdbcConfig)
        assertNull(properties[TeradataConstants.PARAM_SSLMODE])
    }

    @Test
    fun testSSLDefaultMode() {
        val jdbcConfig = createConfig(true)
        val properties: Map<String, String> = destination.getDefaultConnectionProperties(jdbcConfig)
        assertEquals(
            TeradataConstants.REQUIRE,
            properties[TeradataConstants.PARAM_SSLMODE].toString()
        )
    }

    @Test
    fun testSSLAllowMode() {
        val jdbcConfig = createConfig(TeradataConstants.ALLOW)
        val properties: Map<String, String> = destination.getDefaultConnectionProperties(jdbcConfig)
        assertEquals(
            TeradataConstants.ALLOW,
            properties[TeradataConstants.PARAM_SSLMODE].toString()
        )
    }

    @Test
    fun testSSLVerfifyCAMode() {
        val jdbcConfig = createConfig(TeradataConstants.VERIFY_CA)
        val properties: Map<String, String> = destination.getDefaultConnectionProperties(jdbcConfig)
        assertEquals(
            TeradataConstants.VERIFY_CA,
            properties[TeradataConstants.PARAM_SSLMODE].toString()
        )
        assertNotNull(properties[TeradataConstants.PARAM_SSLCA].toString())
    }

    @Test
    fun testSSLVerfifyFullMode() {
        val jdbcConfig = createConfig(TeradataConstants.VERIFY_FULL)
        val properties: Map<String, String> = destination.getDefaultConnectionProperties(jdbcConfig)
        assertEquals(
            TeradataConstants.VERIFY_FULL,
            properties[TeradataConstants.PARAM_SSLMODE].toString()
        )
        assertNotNull(properties[TeradataConstants.PARAM_SSLCA].toString())
    }

    @ParameterizedTest
    @MethodSource("provideQueryBandTestCases")
    fun testQueryBandCustom(queryBandInput: String, expectedQueryBand: String) {
        val baseParameters: Map<String, Any> = baseParameters() // Adjust to your method
        val map_custom_QB: ImmutableMap<String, Any> =
            ImmutableMap.of(TeradataConstants.QUERY_BAND_KEY, queryBandInput)

        val jdbcConfig = Jsons.jsonNode(MoreMaps.merge(map_custom_QB, baseParameters))
        destination.getDefaultConnectionProperties(jdbcConfig)

        assertEquals(expectedQueryBand, destination.queryBand)
    }
}
