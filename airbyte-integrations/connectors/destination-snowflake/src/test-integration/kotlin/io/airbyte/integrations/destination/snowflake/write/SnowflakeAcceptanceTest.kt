/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.getConfigPath
import io.airbyte.integrations.destination.snowflake.cdk.SnowflakeMigratingConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.snowflake.cdk.migrateJson
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.nio.file.Path
import net.snowflake.client.jdbc.SnowflakeTimestampWithTimezone
import org.junit.jupiter.api.Test

internal val CONFIG_PATH = getConfigPath(CONFIG_WITH_AUTH_STAGING)

class SnowflakeInsertAcceptanceTest : SnowflakeAcceptanceTest(configPath = CONFIG_PATH) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

abstract class SnowflakeAcceptanceTest(
    configPath: Path,
    dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(configPath),
        configSpecClass = SnowflakeSpecification::class.java,
        dataDumper =
            SnowflakeDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        destinationCleaner = SnowflakeDataCleaner,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        stringifyUnionObjects = false,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = true,
                numberCanBeLarge = true,
                nestedFloatLosesPrecision = false,
            ),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        dedupChangeUsesDefault = false,
        testSpeedModeStatsEmission = true,
        configUpdater = SnowflakeMigrationConfigurationUpdater(),
        dataChannelMedium = dataChannelMedium,
        dataChannelFormat = dataChannelFormat,
        mismatchedTypesUnrepresentable = false,
    )

object SnowflakeDataCleaner : DestinationCleaner {
    override fun cleanup() {
        val config =
            SnowflakeConfigurationFactory()
                .make(
                    SnowflakeMigratingConfigurationSpecificationSupplier(
                            Files.readString(CONFIG_PATH)
                        )
                        .get()
                )
        val dataSource =
            SnowflakeBeanFactory()
                .snowflakeDataSource(snowflakeConfiguration = config, airbyteEdition = "COMMUNITY")
        dataSource.connection.use { connection ->
            val statement = connection.createStatement()
            val schemas = connection.metaData.getSchemas(null, "TEST_%")
            while (schemas.next()) {
                val schemaName = schemas.getString("TABLE_SCHEMA")
                statement.execute("DROP SCHEMA IF EXISTS \"$schemaName\" CASCADE")
            }
        }
        dataSource.close()
    }
}

fun stringToMeta(metaAsString: String?): OutputRecord.Meta? {
    if (metaAsString.isNullOrEmpty()) {
        return null
    }
    val metaJson = Jsons.readTree(metaAsString)

    val changes =
        (metaJson["changes"] as ArrayNode).map { change ->
            val changeNode = change as JsonNode
            Meta.Change(
                field = changeNode["field"].textValue(),
                change =
                    AirbyteRecordMessageMetaChange.Change.fromValue(
                        changeNode["change"].textValue()
                    ),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(
                        changeNode["reason"].textValue()
                    ),
            )
        }

    return OutputRecord.Meta(
        changes = changes,
        syncId = metaJson["sync_id"].longValue(),
    )
}

class SnowflakeDataDumper(
    private val configProvider: (ConfigurationSpecification) -> SnowflakeConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val dataSource =
            SnowflakeBeanFactory()
                .snowflakeDataSource(snowflakeConfiguration = config, airbyteEdition = "COMMUNITY")

        val output = mutableListOf<OutputRecord>()

        dataSource.let { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val resultSet =
                    statement.executeQuery(
                        "SELECT * FROM \"${stream.mappedDescriptor.namespace}\".\"${stream.mappedDescriptor.name}\""
                    )

                while (resultSet.next()) {
                    val dataMap = linkedMapOf<String, AirbyteValue>()
                    for (i in 1..resultSet.metaData.columnCount) {
                        val columnName = resultSet.metaData.getColumnName(i)
                        if (!Meta.COLUMN_NAMES.contains(columnName)) {
                            val value = resultSet.getObject(i)
                            dataMap[columnName] =
                                value?.let { AirbyteValue.from(convertValue(value)) } ?: NullValue
                        }
                    }
                    val outputRecord =
                        OutputRecord(
                            rawId = resultSet.getString(Meta.COLUMN_NAME_AB_RAW_ID),
                            extractedAt =
                                resultSet
                                    .getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
                                    .toInstant()
                                    .toEpochMilli(),
                            loadedAt = null,
                            generationId = resultSet.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID),
                            data = ObjectValue(dataMap),
                            airbyteMeta =
                                stringToMeta(resultSet.getString(Meta.COLUMN_NAME_AB_META)),
                        )
                    output.add(outputRecord)
                }
            }
        }

        dataSource.close()

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("Snowflake does not support file transfer.")
    }

    private fun convertValue(value: Any): Any =
        when (value) {
            is java.sql.Date -> value.toLocalDate()
            is SnowflakeTimestampWithTimezone -> value.toZonedDateTime()
            is java.sql.Time -> value.toLocalTime()
            is java.sql.Timestamp -> value.toLocalDateTime()
            else -> value
        }
}

class SnowflakeMigrationConfigurationUpdater : ConfigurationUpdater {
    override fun update(config: String): String = migrateJson(config)

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(
            updatedConfig = config.replace("TEXT_SCHEMA", defaultNamespace),
            actualDefaultNamespace = defaultNamespace
        )
}
