/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.Meta
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
import io.airbyte.integrations.destination.postgres.PostgresConfigUpdater
import io.airbyte.integrations.destination.postgres.PostgresContainerHelper
import io.airbyte.integrations.destination.postgres.config.PostgresBeanFactory
import io.airbyte.integrations.destination.postgres.db.PostgresFinalTableNameGenerator
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.spec.PostgresConfigurationFactory
import io.airbyte.integrations.destination.postgres.spec.PostgresSpecification
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import org.junit.jupiter.api.BeforeAll
import org.postgresql.util.PGobject

/**
 * PostgreSQL normalizes timestamptz values to UTC and doesn't preserve the original timezone offset.
 * This mapper converts expected timestamp_with_timezone values to UTC for comparison.
 */
object PostgresTimestampNormalizationMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData = normalizeTimestampsToUtc(expectedRecord.data)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }

    private fun normalizeTimestampsToUtc(value: AirbyteValue): AirbyteValue =
        when (value) {
            is TimestampWithTimezoneValue ->
                TimestampWithTimezoneValue(value.value.withOffsetSameInstant(java.time.ZoneOffset.UTC))
            is ArrayValue -> ArrayValue(value.values.map { normalizeTimestampsToUtc(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) ->
                        normalizeTimestampsToUtc(v)
                    }
                )
            else -> value
        }
}

class PostgresDataDumper(
    private val configProvider: (ConfigurationSpecification) -> PostgresConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val tableNameGenerator = PostgresFinalTableNameGenerator(config)
        val dataSource = PostgresBeanFactory().postgresDataSource(
            postgresConfiguration = config,
            resolvedHost = config.host,
            resolvedPort = config.port
        )

        val output = mutableListOf<OutputRecord>()

        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()

                // Use the FinalTableNameGenerator to get the correct table name
                val tableName = tableNameGenerator.getTableName(stream.mappedDescriptor)
                val quotedTableName = "\"${tableName.namespace}\".\"${tableName.name}\""

                // First check if the table exists
                val tableExistsQuery = """
                    SELECT COUNT(*) AS table_count
                    FROM information_schema.tables
                    WHERE table_schema = '${tableName.namespace}'
                    AND table_name = '${tableName.name}'
                """.trimIndent()

                val existsResultSet = statement.executeQuery(tableExistsQuery)
                existsResultSet.next()
                val tableExists = existsResultSet.getInt("table_count") > 0
                existsResultSet.close()

                if (!tableExists) {
                    // Table doesn't exist, return empty list
                    return output
                }

                val resultSet = statement.executeQuery("SELECT * FROM $quotedTableName")

                while (resultSet.next()) {
                    val dataMap = linkedMapOf<String, AirbyteValue>()
                    for (i in 1..resultSet.metaData.columnCount) {
                        val columnName = resultSet.metaData.getColumnName(i)
                        if (!Meta.COLUMN_NAMES.contains(columnName)) {
                            val columnType = resultSet.metaData.getColumnTypeName(i)
                            val value = when (columnType) {
                                "timestamptz" -> resultSet.getObject(i, java.time.OffsetDateTime::class.java)
                                "timestamp" -> resultSet.getObject(i, java.time.LocalDateTime::class.java)
                                "timetz" -> resultSet.getObject(i, java.time.OffsetTime::class.java)
                                "time" -> resultSet.getObject(i, java.time.LocalTime::class.java)
                                else -> resultSet.getObject(i)
                            }
                            dataMap[columnName] = value?.let {
                                AirbyteValue.from(convertValue(it))
                            } ?: NullValue
                        }
                    }

                    val outputRecord = OutputRecord(
                        rawId = resultSet.getString(Meta.COLUMN_NAME_AB_RAW_ID),
                        extractedAt = resultSet.getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT).toInstant().toEpochMilli(),
                        loadedAt = null,
                        generationId = resultSet.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID),
                        data = ObjectValue(dataMap),
                        airbyteMeta = stringToMeta(resultSet.getString(Meta.COLUMN_NAME_AB_META))
                    )
                    output.add(outputRecord)
                }
                resultSet.close()
            }
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("Postgres does not support file transfer.")
    }

    private fun convertValue(value: Any): Any =
        when (value) {
            // Date/time types are already converted by JDBC with proper getters above
            is java.time.OffsetDateTime -> value
            is java.time.LocalDateTime -> value
            is java.time.OffsetTime -> value
            is java.time.LocalTime -> value
            is java.time.LocalDate -> value
            // Legacy SQL types (shouldn't occur with our specific getters above, but keep as fallback)
            is java.sql.Date -> value.toLocalDate()
            is java.sql.Time -> value.toLocalTime()
            is java.sql.Timestamp -> value.toLocalDateTime()
            // JSONB and JSON types
            is PGobject -> {
                val jsonNode = io.airbyte.commons.json.Jsons.deserialize(value.value!!)
                io.airbyte.commons.json.Jsons.convertValue(jsonNode, Map::class.java)
            }
            else -> value
        }
}

object PostgresDataCleaner : DestinationCleaner {
    override fun cleanup() {
        // TODO: Implement cleanup logic to drop test schemas/tables
        // Similar to ClickhouseDataCleaner or MSSQLDataCleaner
    }
}

class PostgresAcceptanceTest : BasicFunctionalityIntegrationTest(
    configContents = """{
                        "host": "replace_me_host",
                        "port": replace_me_port,
                        "database": "replace_me_database",
                        "schema": "public",
                        "username": "replace_me_username",
                        "password": "replace_me_password"
                    }""",
    configSpecClass = PostgresSpecification::class.java,
    dataDumper = PostgresDataDumper { spec ->
        val configOverrides = buildConfigOverridesForTestContainer()
        PostgresConfigurationFactory().makeWithOverrides(spec as PostgresSpecification, configOverrides)
    },
    destinationCleaner = PostgresDataCleaner,
    isStreamSchemaRetroactive = true,
    dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
    stringifySchemalessObjects = true,
    schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
    schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
    unionBehavior = UnionBehavior.PASS_THROUGH,
    supportFileTransfer = false,
    commitDataIncrementally = false,
    commitDataIncrementallyOnAppend = false,
    commitDataIncrementallyToEmptyDestinationOnAppend = true,
    commitDataIncrementallyToEmptyDestinationOnDedupe = false,
    allTypesBehavior = StronglyTyped(
        integerCanBeLarge = false,
        numberCanBeLarge = true,
        nestedFloatLosesPrecision = true,
        stripsNullBytes = true,
    ),
    unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    nullEqualsUnset = true,
    configUpdater = PostgresConfigUpdater(),
    recordMangler = PostgresTimestampNormalizationMapper,
) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            PostgresContainerHelper.start()
        }

        /** Builds a map of overrides for the test container environment. */
        private fun buildConfigOverridesForTestContainer(): MutableMap<String, String> {
            return mutableMapOf(
                "host" to PostgresContainerHelper.getHost(),
                "port" to PostgresContainerHelper.getPort().toString(),
                "database" to PostgresContainerHelper.getDatabaseName(),
                "username" to PostgresContainerHelper.getUsername(),
                "password" to PostgresContainerHelper.getPassword()
            )
        }
    }
}

fun stringToMeta(metaAsString: String?): OutputRecord.Meta? {
    if (metaAsString.isNullOrEmpty()) {
        return null
    }
    val metaJson = Jsons.readTree(metaAsString)

    val changes = (metaJson["changes"] as ArrayNode).map { change ->
        val changeNode = change as JsonNode
        Meta.Change(
            field = changeNode["field"].textValue(),
            change = AirbyteRecordMessageMetaChange.Change.fromValue(changeNode["change"].textValue()),
            reason = AirbyteRecordMessageMetaChange.Reason.fromValue(changeNode["reason"].textValue())
        )
    }

    return OutputRecord.Meta(
        changes = changes,
        syncId = metaJson["sync_id"].longValue()
    )
}
