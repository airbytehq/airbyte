/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.integration

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.ResultSet
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

object MysqlTestDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val mysqlSpec = spec as MysqlSpecification
        val dataSource = createDataSource(mysqlSpec)

        return dataSource.connection.use { connection ->
            val namespace = stream.mappedDescriptor.namespace
            val tableName = stream.mappedDescriptor.name

            val sql = """SELECT * FROM `$namespace`.`$tableName`"""

            connection.createStatement().use { statement ->
                statement.executeQuery(sql).use { resultSet ->
                    val records = mutableListOf<OutputRecord>()

                    while (resultSet.next()) {
                        records.add(OutputRecord(
                            rawId = resultSet.getString("_airbyte_raw_id"),
                            extractedAt = resultSet.getTimestamp("_airbyte_extracted_at").toInstant().toEpochMilli(),
                            loadedAt = null,
                            generationId = resultSet.getLong("_airbyte_generation_id"),
                            data = extractData(resultSet),
                            airbyteMeta = extractMeta(resultSet),
                        ))
                    }

                    records
                }
            }
        }
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw NotImplementedError("MySQL does not support file transfer")
    }

    private fun createDataSource(spec: MysqlSpecification): DataSource {
        val baseUrl = "jdbc:mysql://${spec.host}:${spec.port}/${spec.database}"
        val sslParam = if (spec.ssl) {
            "sslMode=${spec.sslMode?.value ?: "PREFERRED"}"
        } else {
            "sslMode=DISABLED"
        }
        val jdbcUrl = if (spec.jdbcUrlParams.isNullOrBlank()) {
            "$baseUrl?$sslParam"
        } else {
            "$baseUrl?$sslParam&${spec.jdbcUrlParams}"
        }

        val config = HikariConfig().apply {
            this.jdbcUrl = jdbcUrl
            username = spec.username
            password = spec.password
            driverClassName = "com.mysql.cj.jdbc.Driver"
            maximumPoolSize = 2
        }

        return HikariDataSource(config)
    }

    private fun extractData(resultSet: ResultSet): ObjectValue {
        val metaData = resultSet.metaData
        val columnCount = metaData.columnCount
        val data = linkedMapOf<String, AirbyteValue>()

        for (i in 1..columnCount) {
            val columnName = metaData.getColumnName(i)

            // Skip Airbyte metadata columns
            if (columnName.startsWith("_airbyte_")) {
                continue
            }

            val value = resultSet.getObject(i)
            if (value != null) {
                data[columnName] = AirbyteValue.from(value)
            }
        }

        return ObjectValue(data)
    }

    private fun extractMeta(resultSet: ResultSet): OutputRecord.Meta? {
        val metaJson = resultSet.getString("_airbyte_meta")
        if (metaJson.isNullOrBlank() || metaJson == "{}") {
            return null
        }

        // Parse JSON metadata
        val mapper = com.fasterxml.jackson.databind.ObjectMapper()
        @Suppress("UNCHECKED_CAST")
        val metaMap = mapper.readValue(metaJson, Map::class.java) as Map<String, Any>

        // Extract changes and syncId from the meta map
        @Suppress("UNCHECKED_CAST")
        val changes = (metaMap["changes"] as? List<Map<String, Any>>)?.map { changeMap ->
            io.airbyte.cdk.load.message.Meta.Change(
                field = changeMap["field"] as String,
                change = io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change.fromValue(changeMap["change"] as String),
                reason = io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason.fromValue(changeMap["reason"] as String)
            )
        } ?: emptyList()

        val syncId = (metaMap["sync_id"] as? Number)?.toLong()

        return OutputRecord.Meta(
            changes = changes,
            syncId = syncId
        )
    }
}
