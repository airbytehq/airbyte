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
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.commons.json.Jsons.deserializeExact
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.getConfigPath
import io.airbyte.integrations.destination.snowflake.cdk.SnowflakeMigratingConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.snowflake.cdk.migrateJson
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeSqlNameUtils
import io.airbyte.integrations.destination.snowflake.write.transform.isValid
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import java.math.BigDecimal
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.time.temporal.ChronoUnit
import net.snowflake.client.jdbc.SnowflakeTimestampWithTimezone
import org.junit.jupiter.api.Disabled
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
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
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
        recordMangler = SnowflakeExpectedRecordMapper,
    ) {

    @Disabled override fun testUnions() {}

    @Disabled override fun testAppendJsonSchemaEvolution() {}

    @Disabled override fun testContainerTypes() {}
}

object SnowflakeExpectedRecordMapper : ExpectedRecordMapper {

    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData =
            ObjectValue(
                expectedRecord.data.values
                    .mapValuesTo(linkedMapOf()) { (_, value) -> mapAirbyteValue(value) }
                    .mapKeysTo(linkedMapOf()) { it.key.toSnowflakeCompatibleName() }
            )

        val mappedAirbyteMetadata =
            mapAirbyteMetadata(
                originalData = expectedRecord.data,
                mappedData = mappedData,
                airbyteMetadata = expectedRecord.airbyteMeta
            )
        return expectedRecord.copy(data = mappedData, airbyteMeta = mappedAirbyteMetadata)
    }

    private fun mapAirbyteValue(value: AirbyteValue): AirbyteValue {
        return if (isValid(value)) {
            when (value) {
                is TimeWithTimezoneValue -> StringValue(value.value.toString())
                is ArrayValue,
                is ObjectValue -> StringValue(value.toJson().toPrettyString())
                else -> value
            }
        } else {
            NullValue
        }
    }

    private fun mapAirbyteMetadata(
        originalData: ObjectValue,
        mappedData: ObjectValue,
        airbyteMetadata: OutputRecord.Meta?
    ): OutputRecord.Meta? {
        val nullValues =
        // Find all values that the test has converted to a NullValue because the actual
        // value will fail the validation performed by the SnowflakeValueCoercer at runtime.
        // This excludes any "_ab" prefixed metadata columns or any columns that are already
        // null in the input data for the test.
        mappedData.values.entries.filter {
                !it.key.startsWith("_ab") &&
                    it.value is NullValue &&
                    originalData.values[it.key] != NullValue
            }
        return if (nullValues.isNotEmpty()) {
            // Create a Set of existing change field names for O(1) lookup performance
            val existingChangeFields =
                airbyteMetadata?.changes?.map { it.field }?.toSet() ?: emptySet()

            val changes =
                nullValues
                    // If the field null-ed out by this mapper is already in the input metadata
                    // change list, ignore it.  Otherwise, add it to the collection of changes
                    // to synthesize the validation null-ing of the field.
                    .filter { (k, _) -> !existingChangeFields.contains(k) }
                    .map { (k, _) ->
                        Meta.Change(
                            field = k,
                            change = Change.NULLED,
                            reason =
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    }
            airbyteMetadata?.copy(changes = changes + airbyteMetadata.changes)
                ?: OutputRecord.Meta(changes = changes, syncId = null)
        } else {
            airbyteMetadata
        }
    }
}

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
            val schemas =
                statement.executeQuery(
                    "SHOW SCHEMAS IN DATABASE \"${config.database.toSnowflakeCompatibleName()}\""
                )
            while (schemas.next()) {
                val schemaName = schemas.getString("name")
                val createdOn = schemas.getTimestamp("created_on")
                // Clear all test schemas in the database older than 24 hours
                if (
                    schemaName.startsWith(prefix = "test", ignoreCase = true) &&
                        createdOn.toInstant().isBefore(Instant.now().minus(24, ChronoUnit.HOURS))
                ) {
                    statement.execute("DROP SCHEMA IF EXISTS \"$schemaName\" CASCADE")
                }
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
        val sqlUtils = SnowflakeSqlNameUtils(config)
        val dataSource =
            SnowflakeBeanFactory()
                .snowflakeDataSource(snowflakeConfiguration = config, airbyteEdition = "COMMUNITY")

        val output = mutableListOf<OutputRecord>()

        dataSource.let { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val tableName =
                    TableName(
                        stream.mappedDescriptor.namespace!!.toSnowflakeCompatibleName(),
                        stream.mappedDescriptor.name.toSnowflakeCompatibleName()
                    )

                // First check if the table exists
                val tableExistsQuery =
                    """
                    SELECT COUNT(*) AS TABLE_COUNT
                    FROM information_schema.tables
                    WHERE table_schema = '${tableName.namespace}'
                    AND table_name = '${tableName.name}'
                """.trimIndent()

                val existsResultSet = statement.executeQuery(tableExistsQuery)
                existsResultSet.next()
                val tableExists = existsResultSet.getInt("TABLE_COUNT") > 0
                existsResultSet.close()

                if (!tableExists) {
                    // Table doesn't exist, return empty list
                    return output
                }

                val resultSet =
                    statement.executeQuery(
                        "SELECT * FROM ${sqlUtils.fullyQualifiedName(tableName)}"
                    )

                while (resultSet.next()) {
                    val dataMap = linkedMapOf<String, AirbyteValue>()
                    for (i in 1..resultSet.metaData.columnCount) {
                        val columnName = resultSet.metaData.getColumnName(i)
                        val columnType = resultSet.metaData.getColumnTypeName(i)
                        if (!Meta.COLUMN_NAMES.contains(columnName)) {
                            val value = resultSet.getObject(i)
                            dataMap[columnName] =
                                value?.let {
                                    AirbyteValue.from(
                                        convertValue(
                                            unformatJsonValue(
                                                columnType = columnType,
                                                value = value
                                            )
                                        )
                                    )
                                }
                                    ?: NullValue
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

    private fun unformatJsonValue(columnType: String, value: Any): Any {
        /*
         * Snowflake automatically pretty-prints JSON results for variant, object and array
         * when selecting them via a SQL query.  You can get around this by using the `TO_JSON`
         * function on the column when running the query.  However, we do not have access to the
         * catalog in the dumper to know which columns need to be un-prettied/modified to match
         * the toPrettyString() method of the Jackson JsonNode.  To compensate for this, we will
         * read the JSON string into a JsonNode and then re-pretty-ify it into a string so that
         * it can match what the expected record mapper is doing.
         */
        return when (columnType.lowercase()) {
            "variant",
            "array",
            "object" -> deserializeExact(value.toString()).toPrettyString()
            else -> value
        }
    }

    private fun convertValue(value: Any): Any =
        when (value) {
            is BigDecimal -> value.toBigInteger()
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
