/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.postgres.config.PostgresBeanFactory
import io.airbyte.integrations.destination.postgres.db.PostgresFinalTableNameGenerator
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import org.postgresql.util.PGobject

class PostgresDataDumper(
    private val configProvider: (ConfigurationSpecification) -> PostgresConfiguration
) : DestinationDataDumper {
    private fun sanitizeColumnName(name: String): String {
        // Replicate the sanitization logic used by TableCatalog
        // First normalize Unicode characters (e.g., é -> e)
        var sanitized =
            java.text.Normalizer.normalize(name, java.text.Normalizer.Form.NFD)
                .replace(Regex("\\p{M}"), "") // Remove diacritical marks

        // Replace all non-alphanumeric characters (except underscore) with underscore
        sanitized = sanitized.replace(Regex("[^a-zA-Z0-9_]"), "_")

        // Add underscore prefix if starts with a digit
        if (sanitized.isNotEmpty() && sanitized[0].isDigit()) {
            sanitized = "_$sanitized"
        }

        return sanitized
    }

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val tableNameGenerator = PostgresFinalTableNameGenerator(config)
        val dataSource =
            PostgresBeanFactory()
                .postgresDataSource(
                    postgresConfiguration = config,
                    resolvedHost = config.host,
                    resolvedPort = config.port
                )

        // Build reverse mapping from sanitized column names back to original names
        val reverseMapping = mutableMapOf<String, String>()
        (stream.schema as? io.airbyte.cdk.load.data.ObjectType)?.properties?.keys?.forEach {
            originalName ->
            val sanitizedName = sanitizeColumnName(originalName)
            reverseMapping[sanitizedName] = originalName
        }

        val output = mutableListOf<OutputRecord>()

        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()

                // Use the FinalTableNameGenerator to get the correct table name
                val tableName = tableNameGenerator.getTableName(stream.mappedDescriptor)
                val quotedTableName = "\"${tableName.namespace}\".\"${tableName.name}\""

                // First check if the table exists
                val tableExistsQuery =
                    """
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
                        val sanitizedColumnName = resultSet.metaData.getColumnName(i)
                        if (!Meta.COLUMN_NAMES.contains(sanitizedColumnName)) {
                            // Reverse-map to get the original column name
                            val originalColumnName =
                                reverseMapping[sanitizedColumnName] ?: sanitizedColumnName

                            val columnType = resultSet.metaData.getColumnTypeName(i)
                            val value =
                                when (columnType) {
                                    "timestamptz" ->
                                        resultSet.getObject(i, java.time.OffsetDateTime::class.java)
                                    "timestamp" ->
                                        resultSet.getObject(i, java.time.LocalDateTime::class.java)
                                    "timetz" ->
                                        resultSet.getObject(i, java.time.OffsetTime::class.java)
                                    "time" ->
                                        resultSet.getObject(i, java.time.LocalTime::class.java)
                                    else -> resultSet.getObject(i)
                                }
                            dataMap[originalColumnName] =
                                value?.let { AirbyteValue.from(convertValue(it)) } ?: NullValue
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
                                stringToMeta(resultSet.getString(Meta.COLUMN_NAME_AB_META))
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
            // Legacy SQL types (shouldn't occur with our specific getters above, but keep as
            // fallback)
            is java.sql.Date -> value.toLocalDate()
            is java.sql.Time -> value.toLocalTime()
            is java.sql.Timestamp -> value.toLocalDateTime()
            // JSONB and JSON types
            is PGobject -> {
                val jsonNode = io.airbyte.commons.json.Jsons.deserialize(value.value!!)
                // JSONB can contain objects, arrays, or primitives (strings, numbers, booleans,
                // null)
                // Try to convert to Map if it's an object, otherwise return the primitive value
                when {
                    jsonNode.isObject ->
                        io.airbyte.commons.json.Jsons.convertValue(jsonNode, Map::class.java) as Any
                    jsonNode.isArray ->
                        io.airbyte.commons.json.Jsons.convertValue(jsonNode, List::class.java)
                            as Any
                    jsonNode.isTextual -> jsonNode.asText() ?: ""
                    jsonNode.isNumber ->
                        when {
                            jsonNode.isIntegralNumber -> jsonNode.asLong() as Any
                            else -> jsonNode.asDouble() as Any
                        }
                    jsonNode.isBoolean -> jsonNode.asBoolean() as Any
                    else -> jsonNode.toString()
                }
            }
            else -> value
        }
}
