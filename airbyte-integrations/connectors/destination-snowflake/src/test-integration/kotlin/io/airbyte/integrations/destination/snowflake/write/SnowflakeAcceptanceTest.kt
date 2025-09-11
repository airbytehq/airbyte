package io.airbyte.integrations.destination.snowflake.write

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
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
import io.airbyte.integrations.destination.snowflake.SnowflakeSqlNameTransformer
import io.airbyte.integrations.destination.snowflake.Utils
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.nio.file.Path

class SnowflakeInsertAcceptanceTest : SnowflakeAcceptanceTest(Utils.getConfigPath("secrets/1s1t_internal_staging_config.json"))

abstract class SnowflakeAcceptanceTest(
    private val configPath: Path,
) : BasicFunctionalityIntegrationTest(
    configContents = Files.readString(configPath),
    configSpecClass = SnowflakeSpecification::class.java,
    dataDumper = SnowflakeDataDumper { spec ->
        SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
    },
    destinationCleaner = SnowflakeDataCleaner(configPath),
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
    allTypesBehavior = StronglyTyped(
        integerCanBeLarge = true,
        numberCanBeLarge = true,
        nestedFloatLosesPrecision = false,
    ),
    unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    nullEqualsUnset = true,
    dedupChangeUsesDefault = false,
    testSpeedModeStatsEmission = false,
) {
}

class SnowflakeDataCleaner(private val configPath: Path) : DestinationCleaner {
    override fun cleanup() {
        val config = SnowflakeConfigurationFactory().make(ValidatedJsonUtils.parseOne(SnowflakeSpecification::class.java, Files.readString(configPath)))
        val dataSource = SnowflakeBeanFactory().snowflakeDataSource(config, SnowflakeSqlNameTransformer(), airbyteEdition = "OSS") as HikariDataSource
        dataSource.connection.use { connection ->
            val statement = connection.createStatement()
            val schemas = connection.metaData.getSchemas(null, "TEST_%")
            while (schemas.next()) {
                val schemaName = schemas.getString("TABLE_SCHEM")
                statement.execute("DROP SCHEMA IF EXISTS \"$schemaName\" CASCADE")
            }
        }
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
                    AirbyteRecordMessageMetaChange.Change.fromValue(changeNode["change"].textValue()),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(changeNode["reason"].textValue()),
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
        val dataSource = SnowflakeBeanFactory().snowflakeDataSource(config, SnowflakeSqlNameTransformer(), airbyteEdition = "OSS") as HikariDataSource

        val output = mutableListOf<OutputRecord>()

        dataSource.let { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val resultSet = statement.executeQuery("SELECT * FROM \"${stream.mappedDescriptor.namespace}\".\"${stream.mappedDescriptor.name}\"")

                while (resultSet.next()) {
                    val dataMap = linkedMapOf<String, AirbyteValue>()
                    for (i in 1..resultSet.metaData.columnCount) {
                        val columnName = resultSet.metaData.getColumnName(i)
                        if (!Meta.COLUMN_NAMES.contains(columnName)) {
                            dataMap[columnName] = AirbyteValue.from(resultSet.getObject(i))
                        }
                    }
                    val outputRecord =
                        OutputRecord(
                            rawId = resultSet.getString(Meta.COLUMN_NAME_AB_RAW_ID),
                            extractedAt = resultSet.getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT).toInstant().toEpochMilli(),
                            loadedAt = null,
                            generationId = resultSet.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID),
                            data = ObjectValue(dataMap),
                            airbyteMeta = stringToMeta(resultSet.getString(Meta.COLUMN_NAME_AB_META)),
                        )
                    output.add(outputRecord)
                }
            }
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("Snowflake does not support file transfer.")
    }
}
