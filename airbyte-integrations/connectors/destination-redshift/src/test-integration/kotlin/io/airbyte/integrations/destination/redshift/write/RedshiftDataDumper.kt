/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.schema.RedshiftTableSchemaMapper
import io.airbyte.integrations.destination.redshift.schema.toRedshiftCompatibleName
import io.airbyte.integrations.destination.redshift.sql.RedshiftSqlGenerator
import java.time.ZoneOffset

private val testObjectMapper: ObjectMapper = ObjectMapper()

/**
 * Reads typed (final) tables from Redshift and converts rows to [OutputRecord] objects for test
 * verification. This is the core "read-back" component for acceptance tests.
 */
class RedshiftDataDumper(
    private val configProvider: (ConfigurationSpecification) -> RedshiftConfiguration,
) : DestinationDataDumper {

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val schemaMapper =
            RedshiftTableSchemaMapper(
                config,
                DefaultTempTableNameGenerator(),
            )

        // Build reverse mapping from sanitized column names back to original names
        val reverseMapping = mutableMapOf<String, String>()
        stream.tableSchema.columnSchema.inputSchema.keys.forEach { originalName ->
            val sanitizedName = originalName.toRedshiftCompatibleName()
            reverseMapping[sanitizedName] = originalName
        }

        val output = mutableListOf<OutputRecord>()

        val dataSource = RedshiftTestDataSourceProvider.get()
        dataSource.connection.use { connection ->
            val statement = connection.createStatement()

            // Use the TableSchemaMapper to get the correct table name
            val tableName = schemaMapper.toFinalTableName(stream.mappedDescriptor)
            val sqlGenerator = RedshiftSqlGenerator(config)
            val quotedTableName = sqlGenerator.getFullyQualifiedName(tableName)
            val existsResultSet = statement.executeQuery(sqlGenerator.tableExists(tableName))
            existsResultSet.next()
            val tableExists = existsResultSet.getBoolean(1)
            existsResultSet.close()

            if (!tableExists) {
                return output
            }

            val resultSet = statement.executeQuery("SELECT * FROM $quotedTableName")

            while (resultSet.next()) {
                val dataMap = linkedMapOf<String, AirbyteValue>()
                for (i in 1..resultSet.metaData.columnCount) {
                    val columnName = resultSet.metaData.getColumnName(i)
                    if (!Meta.COLUMN_NAMES.contains(columnName)) {
                        // Reverse-map to get the original column name
                        val originalColumnName = reverseMapping[columnName] ?: columnName

                        val columnType = resultSet.metaData.getColumnTypeName(i).lowercase()
                        val value = readColumnValue(resultSet, i, columnType)
                        dataMap[originalColumnName] =
                            value?.let { AirbyteValue.from(it) } ?: NullValue
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
                            stringToMeta(
                                resultSet.getString(Meta.COLUMN_NAME_AB_META),
                            ),
                    )
                output.add(outputRecord)
            }
            resultSet.close()
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): Map<String, String> {
        throw UnsupportedOperationException("Redshift does not support file transfer.")
    }

    /** Reads a single column value from a ResultSet, applying Redshift-specific type conversions */
    private fun readColumnValue(
        rs: java.sql.ResultSet,
        index: Int,
        typeName: String,
    ): Any? =
        when (typeName) {
            "timestamptz" -> rs.getTimestamp(index)?.let { it.toInstant().atOffset(ZoneOffset.UTC) }
            "timestamp" -> rs.getTimestamp(index)?.toLocalDateTime()
            "date" -> rs.getDate(index)?.toLocalDate()
            "time" -> rs.getTime(index)?.toLocalTime()
            "timetz" ->
                rs.getString(index)?.let {
                    java.time.OffsetTime.parse("${it}:00").withOffsetSameInstant(ZoneOffset.UTC)
                }
            "super" -> rs.getString(index)?.let { json -> parseSuperValue(json) }
            "numeric" -> rs.getBigDecimal(index)
            else -> rs.getObject(index)
        }

    /** Parses a Redshift SUPER column JSON string into Java objects for [AirbyteValue.from] */
    private fun parseSuperValue(json: String): Any? {
        val parsed = testObjectMapper.readTree(json)
        return when {
            parsed.isObject -> testObjectMapper.convertValue(parsed, Map::class.java) as Any
            parsed.isArray -> testObjectMapper.convertValue(parsed, List::class.java) as Any
            parsed.isTextual -> parsed.asText()
            parsed.isNumber ->
                when {
                    parsed.isIntegralNumber -> parsed.asLong() as Any
                    else -> parsed.asDouble() as Any
                }
            parsed.isBoolean -> parsed.asBoolean() as Any
            parsed.isNull -> null
            else -> parsed.toString()
        }
    }
}
