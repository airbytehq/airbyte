/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.db.SnowflakeFinalTableNameGenerator
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeSqlNameUtils
import io.airbyte.integrations.destination.snowflake.sql.sqlEscape
import java.math.BigDecimal
import net.snowflake.client.jdbc.SnowflakeTimestampWithTimezone

private val AIRBYTE_META_COLUMNS = Meta.COLUMN_NAMES + setOf(CDC_DELETED_AT_COLUMN)

class SnowflakeDataDumper(
    private val configProvider: (ConfigurationSpecification) -> SnowflakeConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val sqlUtils = SnowflakeSqlNameUtils(config)
        val snowflakeFinalTableNameGenerator = SnowflakeFinalTableNameGenerator(config)
        val dataSource =
            SnowflakeBeanFactory()
                .snowflakeDataSource(snowflakeConfiguration = config, airbyteEdition = "COMMUNITY")

        val output = mutableListOf<OutputRecord>()

        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val tableName =
                    snowflakeFinalTableNameGenerator.getTableName(stream.mappedDescriptor)

                // First check if the table exists
                val tableExistsQuery =
                    """
                    SELECT COUNT(*) AS TABLE_COUNT
                    FROM information_schema.tables
                    WHERE table_schema = '${sqlEscape(tableName.namespace.replace("\"\"", "\""))}'
                    AND table_name = '${sqlEscape(tableName.name.replace("\"\"", "\""))}'
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
                        if (!AIRBYTE_META_COLUMNS.contains(columnName.lowercase())) {
                            val value = resultSet.getObject(i)
                            dataMap[columnName.toSnowflakeCompatibleName()] =
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
                            rawId =
                                resultSet.getString(
                                    Meta.COLUMN_NAME_AB_RAW_ID.toSnowflakeCompatibleName()
                                ),
                            extractedAt =
                                resultSet
                                    .getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT.uppercase())
                                    .toInstant()
                                    .toEpochMilli(),
                            loadedAt = null,
                            generationId =
                                resultSet.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID.uppercase()),
                            data = ObjectValue(dataMap),
                            airbyteMeta =
                                stringToMeta(
                                    resultSet.getString(Meta.COLUMN_NAME_AB_META.uppercase())
                                ),
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

    private fun unformatJsonValue(columnType: String, value: Any): Any {
        return when (columnType.lowercase()) {
            "variant",
            "array",
            "object" ->
                // blind cast to string is safe - snowflake JDBC driver getObject returns String
                // for variant/array/object
                (value as String).deserializeToNode().toAirbyteValue()
            else -> value
        }
    }

    private fun convertValue(value: Any?): Any? =
        when (value) {
            is BigDecimal -> value.toBigInteger()
            is java.sql.Date -> value.toLocalDate()
            is SnowflakeTimestampWithTimezone -> value.toZonedDateTime()
            is java.sql.Time -> value.toLocalTime()
            is java.sql.Timestamp -> value.toLocalDateTime()
            else -> value
        }
}
