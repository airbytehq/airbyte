/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.snowflake

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import io.airbyte.integrations.sourceTesting.JdbcTestDbExecutor
import io.airbyte.integrations.sourceTesting.TestDbExecutor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File

class SnowflakeTestDbExecutor(configFilePath: String, assetName: String) : TestDbExecutor {

    private val jdbcExecutor =
        JdbcTestDbExecutor(
            assetName = assetName,
            jdbcConfig = createSnowflakeConfiguration(configFilePath)
        )

    override val assetName: String = assetName

    override fun executeReadQuery(query: String): List<Map<String, Any?>> =
        jdbcExecutor.executeReadQuery(query)

    override fun executeUpdate(query: String) = jdbcExecutor.executeUpdate(query)

    override fun close() = jdbcExecutor.close()

    companion object {
        private val log = KotlinLogging.logger {}
        private val objectMapper = jacksonObjectMapper()

        fun createSnowflakeConfiguration(configFilePath: String): SnowflakeSourceConfiguration {
            log.info { "Loading Snowflake test configuration from: $configFilePath" }

            val configFile = File(configFilePath)
            if (!configFile.exists()) {
                throw IllegalArgumentException("Config file not found: $configFilePath")
            }

            val configJson: JsonNode = objectMapper.readTree(configFile)
            val configSpec =
                objectMapper.treeToValue(
                    configJson,
                    SnowflakeSourceConfigurationSpecification::class.java
                )

            val configFactory = SnowflakeSourceConfigurationFactory()
            return configFactory.make(configSpec)
        }
    }
}
