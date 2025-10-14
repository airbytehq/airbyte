/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.db.SnowflakeFinalTableNameGenerator
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeSqlNameUtils

class SnowflakeRawDataDumper(
    private val configProvider: (ConfigurationSpecification) -> SnowflakeConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val output = mutableListOf<OutputRecord>()

        val config = configProvider(spec)
        val sqlUtils = SnowflakeSqlNameUtils(config)
        val snowflakeFinalTableNameGenerator = SnowflakeFinalTableNameGenerator(config)
        val dataSource =
            SnowflakeBeanFactory()
                .snowflakeDataSource(snowflakeConfiguration = config, airbyteEdition = "COMMUNITY")

        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val tableName =
                    snowflakeFinalTableNameGenerator.getTableName(stream.mappedDescriptor)

                val resultSet =
                    statement.executeQuery(
                        "SELECT * FROM ${sqlUtils.fullyQualifiedName(tableName)}"
                    )

                while (resultSet.next()) {
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
                            data =
                                StringValue(resultSet.getString(Meta.COLUMN_NAME_DATA))
                                    .value
                                    .deserializeToNode()
                                    .toAirbyteValue(),
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
}
