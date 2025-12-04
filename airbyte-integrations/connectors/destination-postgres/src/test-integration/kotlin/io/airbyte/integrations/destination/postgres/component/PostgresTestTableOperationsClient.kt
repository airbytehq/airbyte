/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import javax.sql.DataSource

@Requires(env = ["component"])
@Singleton
class PostgresTestTableOperationsClient(
    private val dataSource: DataSource,
) : TestTableOperationsClient {

    override suspend fun ping() {
        dataSource.connection.use { connection ->
            connection.createStatement().use { stmt -> stmt.execute("SELECT 1") }
        }
    }

    override suspend fun dropNamespace(namespace: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { stmt ->
                stmt.execute("DROP SCHEMA IF EXISTS \"$namespace\" CASCADE")
            }
        }
    }

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        if (records.isEmpty()) return

        dataSource.connection.use { connection ->
            // Use PostgreSQL's ability to insert JSON directly
            val sql =
                """
                INSERT INTO "${table.namespace}"."${table.name}"
                SELECT * FROM json_populate_recordset(
                    null::"${table.namespace}"."${table.name}",
                    ?::json
                )
                """.trimIndent()

            connection.prepareStatement(sql).use { stmt ->
                stmt.setString(1, records.serializeToString())
                stmt.executeUpdate()
            }
        }
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        val records = mutableListOf<Map<String, Any>>()

        dataSource.connection.use { connection ->
            val sql = "SELECT * FROM \"${table.namespace}\".\"${table.name}\""
            connection.createStatement().use { stmt ->
                stmt.executeQuery(sql).use { rs ->
                    val metaData = rs.metaData
                    val columnCount = metaData.columnCount

                    while (rs.next()) {
                        val record = mutableMapOf<String, Any>()
                        for (i in 1..columnCount) {
                            val columnName = metaData.getColumnName(i)
                            val value = rs.getObject(i)
                            if (value != null) {
                                record[columnName] = normalizeValue(value)
                            }
                        }
                        records.add(record)
                    }
                }
            }
        }

        return records
    }

    private fun normalizeValue(value: Any): Any {
        return when (value) {
            is java.sql.Timestamp -> value.toInstant().toString()
            is java.time.OffsetDateTime -> value.toInstant().toString()
            is org.postgresql.util.PGobject -> {
                // Handle JSONB and other PostgreSQL-specific types
                when (value.type) {
                    "jsonb",
                    "json" -> {
                        // Parse JSON and return appropriate type
                        val jsonStr = value.value ?: "{}"
                        try {
                            io.airbyte.cdk.load.util.Jsons.readTree(jsonStr).let { node ->
                                when {
                                    node.isObject -> {
                                        val map = linkedMapOf<String, Any?>()
                                        node.fields().forEach { (k, v) ->
                                            map[k] =
                                                when {
                                                    v.isNull -> null
                                                    v.isTextual -> v.textValue()
                                                    v.isNumber -> v.numberValue()
                                                    v.isBoolean -> v.booleanValue()
                                                    else -> v.toString()
                                                }
                                        }
                                        map
                                    }
                                    node.isTextual -> node.textValue()
                                    node.isNumber -> node.numberValue()
                                    node.isBoolean -> node.booleanValue()
                                    node.isArray -> jsonStr // Keep array as string for comparison
                                    else -> jsonStr
                                }
                            }
                        } catch (e: Exception) {
                            jsonStr
                        }
                    }
                    else -> value.value ?: ""
                }
            }
            is java.math.BigDecimal -> value.toLong()
            is java.math.BigInteger -> value.toLong()
            is Short -> value.toLong()
            is Int -> value.toLong()
            else -> value
        }
    }
}
