/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.snowflake

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.integrations.sourceTesting.ColumnDefinition
import io.airbyte.integrations.sourceTesting.ColumnType
import io.airbyte.integrations.sourceTesting.TableDefinition
import io.airbyte.integrations.sourceTesting.TestAssetResourceNamer
import io.airbyte.integrations.sourceTesting.tests.FullRefreshTest
import java.io.File

@Suppress("UNCHECKED_CAST")
class SnowflakeSourceFullRefreshTest :
    FullRefreshTest(
        testDbExecutor = createTestDbExecutor(),
        testAssetResourceNamer = createTestAssetResourceNamer()
    ) {

    override val sqlDialect = SnowflakeSqlDialect()
    override val streamFactory = SnowflakeSourceOperations()
    override val configFactory:
        SourceConfigurationFactory<ConfigurationSpecification, SourceConfiguration> =
        SnowflakeSourceConfigurationFactory()
            as SourceConfigurationFactory<ConfigurationSpecification, SourceConfiguration>
    override var config: ConfigurationSpecification = loadTestConfiguration()

    override fun setupTablesForAllNamespaces(num: Int) {
        for (namespace in namespaces) {
            for (i in 1..num) {
                val tableName = testAssetResourceNamer.getName()
                val colId =
                    ColumnDefinition(
                        name = "id",
                        type = ColumnType.BIGINT,
                        jdbcType = BigDecimalFieldType,
                        isPrimaryKey = true,
                        isNullable = false,
                    )
                val colName =
                    ColumnDefinition(
                        name = "name",
                        type = ColumnType.VARCHAR,
                        jdbcType = StringFieldType,
                        length = 255,
                        isNullable = false,
                    )
                val colCreatedAt =
                    ColumnDefinition(
                        name = "created_at",
                        type = ColumnType.TIMESTAMP,
                        jdbcType = LocalDateTimeFieldType,
                        isNullable = false,
                        defaultValue = "CURRENT_TIMESTAMP",
                    )
                val table =
                    TableDefinition(
                        tableName = tableName,
                        columns = listOf(colId, colName, colCreatedAt),
                        namespace = namespace,
                    )
                tables.putIfAbsent(namespace, mutableListOf())
                tables[namespace]!!.add(table)
                testDbExecutor.executeUpdate(sqlDialect.buildCreateTableQuery(table))
            }
        }
    }

    companion object {
        private const val CONFIG_FILE_PATH = "secrets/config_test.json"
        private val testAssetResourceNamer = TestAssetResourceNamer()

        private fun createTestAssetResourceNamer(): TestAssetResourceNamer = testAssetResourceNamer

        private fun createTestDbExecutor(): SnowflakeTestDbExecutor {
            return SnowflakeTestDbExecutor(CONFIG_FILE_PATH, testAssetResourceNamer.getName())
        }

        private fun loadTestConfiguration(): SnowflakeSourceConfigurationSpecification {
            val configFile = File(CONFIG_FILE_PATH)
            if (!configFile.exists()) {
                throw NoSuchElementException(
                    "Secret config file not found. If you are running this test locally, please follow https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/ci_credentials/README.md#get-gsm-access to set up required config."
                )
            }

            val objectMapper = jacksonObjectMapper()
            val configJson = objectMapper.readTree(configFile)
            return objectMapper.treeToValue(
                configJson,
                SnowflakeSourceConfigurationSpecification::class.java
            )
        }
    }
}
