/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.sql.Date
import java.sql.ResultSet
import java.sql.Timestamp
import java.sql.Types
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import javax.sql.DataSource

/**
 * JDBC-based [TestTableOperationsClient] for Databricks component tests. Handles
 * Databricks-specific type conversions for inserts and reads using backtick-quoted identifiers.
 */
@Requires(env = ["component"])
@Singleton
class DatabricksTestTableOperationsClient(
    private val dataSource: DataSource,
    private val config: DatabricksV2Configuration,
) : TestTableOperationsClient {

    private fun fqn(table: TableName): String =
        "`${config.database}`.`${table.namespace}`.`${table.name}`"

    override suspend fun ping() {
        dataSource.connection.use { conn -> conn.createStatement().use { it.execute("SELECT 1") } }
    }

    override suspend fun dropNamespace(namespace: String) {
        dataSource.connection.use { conn ->
            conn.createStatement().use {
                it.execute("DROP SCHEMA IF EXISTS `${config.database}`.`$namespace` CASCADE")
            }
        }
    }

    override suspend fun insertRecords(
        table: TableName,
        records: List<Map<String, AirbyteValue>>,
    ) {
        if (records.isEmpty()) return

        val columnTypes = getColumnTypes(table)
        val columns = records.flatMap { it.keys }.distinct().toList()
        val columnNames = columns.joinToString(", ") { "`$it`" }
        val placeholders = columns.indices.joinToString(", ") { "?" }

        dataSource.connection.use { conn ->
            conn
                .prepareStatement("INSERT INTO ${fqn(table)} ($columnNames) VALUES ($placeholders)")
                .use { ps ->
                    for (record in records) {
                        columns.forEachIndexed { index, column ->
                            setParameterValue(ps, index + 1, record[column], columnTypes[column])
                        }
                        ps.addBatch()
                    }
                    ps.executeBatch()
                }
        }
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery("SELECT * FROM ${fqn(table)}").use { rs ->
                    val meta = rs.metaData
                    return buildList {
                        while (rs.next()) {
                            add(
                                buildMap {
                                    for (i in 1..meta.columnCount) {
                                        val value =
                                            readColumn(rs, i, meta.getColumnTypeName(i).uppercase())
                                        if (value != null) put(meta.getColumnName(i), value)
                                    }
                                }
                            )
                        }
                    }
                }
            }
        }
    }

    private fun getColumnTypes(table: TableName): Map<String, String> {
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt
                    .executeQuery(
                        """
                        SELECT column_name, data_type
                        FROM ${config.database}.information_schema.columns
                        WHERE table_catalog = '${config.database}'
                          AND table_schema = '${table.namespace}'
                          AND table_name = '${table.name}'
                        """.trimIndent(),
                    )
                    .use { rs ->
                        return buildMap {
                            while (rs.next()) {
                                put(rs.getString("column_name"), rs.getString("data_type"))
                            }
                        }
                    }
            }
        }
    }

    private fun setParameterValue(
        ps: java.sql.PreparedStatement,
        index: Int,
        value: AirbyteValue?,
        columnType: String?,
    ) {
        if (value == null || value is NullValue) {
            ps.setNull(index, Types.VARCHAR)
            return
        }

        // STRING columns: serialize everything as string (handles JSON objects/arrays/unions/times)
        if (columnType?.uppercase() == "STRING") {
            ps.setString(index, serializeValue(value))
            return
        }

        when (value) {
            is StringValue -> ps.setString(index, value.value)
            is IntegerValue -> ps.setLong(index, value.value.toLong())
            is NumberValue -> ps.setBigDecimal(index, value.value)
            is BooleanValue -> ps.setBoolean(index, value.value)
            is TimestampWithTimezoneValue ->
                ps.setTimestamp(index, Timestamp.from(value.value.toInstant()))
            is TimestampWithoutTimezoneValue ->
                ps.setTimestamp(
                    index,
                    Timestamp.from(value.value.toInstant(ZoneOffset.UTC)),
                )
            is DateValue -> ps.setDate(index, Date.valueOf(value.value))
            is TimeWithTimezoneValue -> ps.setString(index, value.value.toString())
            is TimeWithoutTimezoneValue -> ps.setString(index, value.value.toString())
            is ObjectValue -> ps.setString(index, Jsons.writeValueAsString(value.values))
            is ArrayValue -> ps.setString(index, Jsons.writeValueAsString(value.values))
            else -> throw IllegalArgumentException("Unsupported AirbyteValue: $value")
        }
    }

    private fun serializeValue(value: AirbyteValue): String =
        when (value) {
            is NullValue -> "null"
            is StringValue -> value.value
            is IntegerValue -> value.value.toString()
            is NumberValue -> value.value.toPlainString()
            is BooleanValue -> value.value.toString()
            is ObjectValue -> Jsons.writeValueAsString(value.values)
            is ArrayValue -> Jsons.writeValueAsString(value.values)
            is DateValue -> value.value.toString()
            is TimestampWithTimezoneValue -> value.value.toString()
            is TimestampWithoutTimezoneValue -> value.value.toString()
            is TimeWithTimezoneValue -> value.value.toString()
            is TimeWithoutTimezoneValue -> value.value.toString()
        }

    private fun readColumn(rs: ResultSet, index: Int, typeName: String): Any? {
        rs.getObject(index) ?: return null
        return when (typeName) {
            "TIMESTAMP" ->
                rs.getTimestamp(index)
                    ?.toInstant()
                    ?.atOffset(ZoneOffset.UTC)
                    ?.format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
            "TIMESTAMP_NTZ" -> rs.getTimestamp(index)?.toLocalDateTime()?.toString()
            "DATE" -> rs.getDate(index)?.toString()
            "LONG",
            "BIGINT",
            "INT" -> rs.getLong(index)
            "DECIMAL" -> rs.getBigDecimal(index) ?: BigDecimal.ZERO
            "BOOLEAN" -> rs.getBoolean(index)
            "STRING" -> rs.getString(index)
            else -> rs.getObject(index)
        }
    }
}
