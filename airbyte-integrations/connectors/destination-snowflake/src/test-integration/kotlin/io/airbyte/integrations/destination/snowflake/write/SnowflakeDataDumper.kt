/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.commons.json.Jsons.deserializeExact
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.db.SnowflakeFinalTableNameGenerator
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeSqlNameUtils
import java.math.BigDecimal
import net.snowflake.client.jdbc.SnowflakeTimestampWithTimezone

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
