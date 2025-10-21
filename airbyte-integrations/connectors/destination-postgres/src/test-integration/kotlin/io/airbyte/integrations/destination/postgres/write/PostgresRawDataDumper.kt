/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.postgres.config.PostgresBeanFactory
import io.airbyte.integrations.destination.postgres.db.PostgresFinalTableNameGenerator
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration

class PostgresRawDataDumper(
    private val configProvider: (ConfigurationSpecification) -> PostgresConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val output = mutableListOf<OutputRecord>()

        val config = configProvider(spec)
        val tableNameGenerator = PostgresFinalTableNameGenerator(config)
        val dataSource = PostgresBeanFactory().postgresDataSource(
            postgresConfiguration = config,
            resolvedHost = config.host,
            resolvedPort = config.port
        )

        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val tableName = tableNameGenerator.getTableName(stream.mappedDescriptor)
                val quotedTableName = "\"${tableName.namespace}\".\"${tableName.name}\""

                // Check if table exists first
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
                    // Get JSONB data - PostgreSQL returns it as a PGobject
                    val dataObject = resultSet.getObject(Meta.COLUMN_NAME_DATA)
                    val dataJson = when (dataObject) {
                        is org.postgresql.util.PGobject -> dataObject.value
                        else -> dataObject?.toString() ?: "{}"
                    }

                    val outputRecord = OutputRecord(
                        rawId = resultSet.getString(Meta.COLUMN_NAME_AB_RAW_ID),
                        extractedAt = resultSet.getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT).toInstant().toEpochMilli(),
                        loadedAt = null,
                        generationId = resultSet.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID),
                        data = dataJson
                            ?.deserializeToNode()
                            ?.toAirbyteValue() ?: NullValue,
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
}
